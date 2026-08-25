import json, httpx

payload = {
    "model": "helios-gemma4",
    "messages": [
        {"role": "system", "content": "You are HELIOS. Return only data conforming to the supplied schema."},
        {"role": "user", "content": "Return a review-gated test result. Invent no evidence and no numbers."}
    ],
    "temperature": 0.1,
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "helios_intelligence_answer",
            "strict": False,
            "schema": {
                "type": "object",
                "properties": {
                    "decision_status": {"type": "string"},
                    "headline": {"type": "string"},
                    "summary": {"type": "string"},
                    "recommended_actions": {"type": "array"},
                    "uncertainties": {"type": "array", "items": {"type": "string"}},
                    "evidence_refs": {"type": "array", "items": {"type": "string"}},
                    "numeric_claims": {"type": "object"},
                    "requires_human_review": {"type": "boolean"}
                },
                "required": [
                    "decision_status", "headline", "summary",
                    "recommended_actions", "uncertainties",
                    "evidence_refs", "numeric_claims",
                    "requires_human_review"
                ]
            }
        }
    }
}

with httpx.Client(timeout=180.0) as c:
    r = c.post("http://127.0.0.1:1235/v1/chat/completions", json=payload)
    print("HTTP", r.status_code)
    print(r.text[:8000])
    assert r.status_code == 200, r.text
    data = r.json()
    content = data["choices"][0]["message"]["content"]
    obj = json.loads(content)
    assert obj.get("requires_human_review") is True
    print("PASS: LM Studio json_schema structured output")
