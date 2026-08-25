import json
from app.db.session import SessionLocal
from app.realdata.service import sync_osm

db = SessionLocal()
try:
    run = sync_osm(db, "phx-downtown")
    print(json.dumps({
        "run_id": run.id,
        "provider": run.provider,
        "status": run.status,
        "truth_category": run.truth_category,
        "records_received": run.records_received,
        "records_applied": run.records_applied,
        "details": run.details_json,
    }, indent=2))
finally:
    db.close()
