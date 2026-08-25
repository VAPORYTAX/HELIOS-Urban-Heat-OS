import json
from app.db.session import SessionLocal
from app.quality.service import run_quality_snapshot

db = SessionLocal()
try:
    r = run_quality_snapshot(db, "phx-downtown", fortyguard_live=False)
    print(json.dumps({
        "area_id": r.area_id,
        "status": r.status,
        "health_score": r.health_score,
        "requires_human_review": r.requires_human_review,
        "checks": r.checks_json,
    }, indent=2, default=str))
finally:
    db.close()
