import json
from app.db.session import SessionLocal
from app.realdata.census import status
from app.realdata.demographics import sync_census_demographics

print(json.dumps({"census_readiness": status()}, indent=2))
db = SessionLocal()
try:
    run = sync_census_demographics(db, "phx-downtown")
    print(json.dumps({
        "run_id": run.id,
        "provider": run.provider,
        "status": run.status,
        "records_received": run.records_received,
        "records_applied": run.records_applied,
        "details": run.details_json,
    }, indent=2))
finally:
    db.close()
