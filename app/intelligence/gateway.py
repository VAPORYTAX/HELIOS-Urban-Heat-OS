from __future__ import annotations
import json, time
import httpx

from app.intelligence.config import settings
from app.intelligence.contracts import IntelligenceAnswer

def _helios_response_format():
    schema = IntelligenceAnswer.model_json_schema()
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "helios_intelligence_answer",
            "strict": True,
            "schema": schema,
        },
    }

def readiness() -> dict:
    cfg = settings()
    if not cfg["enabled"]:
        return {"enabled": False, "reachable": False, "model": cfg["model"], "base_url": cfg["base_url"]}
    try:
        with httpx.Client(timeout=3.0) as client:
            r = client.get(cfg["base_url"] + "/models")
            reachable = r.status_code < 500
            models = r.json().get("data", []) if reachable else []
    except Exception:
        reachable = False
        models = []
    return {
        "enabled": cfg["enabled"],
        "reachable": reachable,
        "model": cfg["model"],
        "fallback_model": cfg["fallback_model"],
        "base_url": cfg["base_url"],
        "available_models": [m.get("id") for m in models if isinstance(m, dict)],
    }

def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    # Strip Gemma thought-channel material defensively if server surfaces it.
    if "<|channel>final" in text:
        text = text.split("<|channel>final", 1)[-1]
    if "<channel|>" in text:
        text = text.split("<channel|>")[-1]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("model returned no JSON object")
    return json.loads(text[start:end+1])

def chat(*, model: str, messages: list[dict], thinking: bool, timeout: float | None = None, max_tokens: int | None = None, temperature: float | None = None) -> tuple[dict, float]:
    cfg = settings()
    system_prefix = "<|think|>\n" if thinking else ""
    msgs = []
    for i, m in enumerate(messages):
        if i == 0 and m.get("role") == "system":
            msgs.append({"role":"system","content":system_prefix + m.get("content","")})
        else:
            msgs.append(m)

    payload = {
        "model": model,
        "messages": msgs,
        "temperature": 0.2 if temperature is None else temperature,
        "top_p": 0.90,
        "response_format": _helios_response_format(),
    }
    if max_tokens is not None:
        payload["max_tokens"] = int(max_tokens)
    started = time.perf_counter()
    with httpx.Client(timeout=timeout or cfg["timeout_seconds"]) as client:
        r = client.post(cfg["base_url"] + "/chat/completions", json=payload)
        if r.status_code >= 400:
            raise RuntimeError(f"LM Studio chat error HTTP {r.status_code}: {r.text[:4000]}")
        data = r.json()
    elapsed = (time.perf_counter() - started) * 1000.0
    text = data["choices"][0]["message"]["content"]
    return _extract_json(text), elapsed


def chat_native_fast(*, model_key: str, messages: list[dict], timeout: float = 120.0, max_output_tokens: int = 900, temperature: float = 0.2) -> tuple[dict, float]:
    """LM Studio native FAST path with reasoning explicitly disabled."""
    cfg = settings()
    base = cfg["base_url"]
    if base.endswith("/v1"):
        base = base[:-3]

    system_parts = []
    user_parts = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "system":
            system_parts.append(content)
        else:
            user_parts.append(content)

    payload = {
        "model": model_key,
        "system_prompt": "\n\n".join(system_parts),
        "input": "\n\n".join(user_parts),
        "reasoning": "off",
        "temperature": temperature,
        "max_output_tokens": int(max_output_tokens),
        "context_length": 8192,
        "store": False,
        "stream": False,
    }

    import time
    started = time.perf_counter()
    with httpx.Client(timeout=timeout) as client:
        r = client.post(base + "/api/v1/chat", json=payload)
        r.raise_for_status()
        body = r.json()
    latency_ms = (time.perf_counter() - started) * 1000.0

    output = body.get("output", [])
    chunks = [
        x.get("content", "")
        for x in output
        if isinstance(x, dict) and x.get("type") == "message"
    ]
    text = "\n".join(chunks).strip()
    if not text:
        raise ValueError("native model returned no message content")
    obj = _extract_json(text)
    if isinstance(obj, dict) and isinstance(obj.get("uncertainties"), str):
        obj["uncertainties"] = [obj["uncertainties"]]
    return obj, latency_ms
