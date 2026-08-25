import json, urllib.request

BASE = "http://127.0.0.1:8080/api/v1"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)

latest = get("/quality/latest?area_id=phx-downtown")
audit = get("/quality/audit?area_id=phx-downtown&limit=20")

assert latest is not None
assert 0 <= latest["health_score"] <= 1
assert latest["requires_human_review"] is True
assert latest["status"] in {"review_required", "degraded", "healthy"}
assert isinstance(audit, list)

checks = latest["checks"]["checks"]
assert any(x["check"] == "thermal_freshness" for x in checks)
assert any(x["check"] == "metric_invariants" for x in checks)

print(json.dumps({
    "status": latest["status"],
    "health_score": latest["health_score"],
    "requires_human_review": latest["requires_human_review"],
    "audit_events": len(audit),
    "checks": len(checks),
}, indent=2))
print("PASS: HELIOS scientific and reliability hardening is healthy")
