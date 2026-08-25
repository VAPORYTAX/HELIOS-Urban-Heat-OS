from __future__ import annotations
import os
from pathlib import Path

def _env_file() -> dict[str, str]:
    p = Path(r"D:\HELIOS\.env")
    if not p.exists():
        return {}
    out = {}
    for raw in p.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def _get(name: str, default: str) -> str:
    return os.getenv(name) or _env_file().get(name) or default

def settings():
    return {
        "base_url": _get("GEMMA_BASE_URL", "http://127.0.0.1:1235/v1").rstrip("/"),
        "model": _get("GEMMA_MODEL", "gemma-4-26B-A4B-it"),
        "fallback_model": _get("GEMMA_FALLBACK_MODEL", "gemma-4-12B-it"),
        "timeout_seconds": float(_get("GEMMA_TIMEOUT_SECONDS", "120")),
        "enabled": _get("GEMMA_ENABLED", "true").lower() in {"1","true","yes","on"},
    }
