from __future__ import annotations
from datetime import datetime, timezone

def age_hours(ts: datetime | None, now: datetime | None = None) -> float | None:
    if ts is None:
        return None
    now = now or datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return max(0.0, (now - ts).total_seconds() / 3600.0)

def thermal_freshness(ts: datetime | None, provider_live: bool) -> dict:
    age = age_hours(ts)
    if age is None:
        return {"status": "missing", "score": 0.0, "age_hours": None}
    if not provider_live:
        return {"status": "fixture_or_nonlive", "score": 0.45, "age_hours": age}
    if age <= 3:
        return {"status": "fresh", "score": 1.0, "age_hours": age}
    if age <= 12:
        return {"status": "aging", "score": 0.75, "age_hours": age}
    if age <= 24:
        return {"status": "stale", "score": 0.45, "age_hours": age}
    return {"status": "expired", "score": 0.15, "age_hours": age}
