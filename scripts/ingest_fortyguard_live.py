import json
from app.db.session import SessionLocal
from app.fortyguard_live.service import ingest_live_hour
db=SessionLocal()
try:
    r=ingest_live_hour(db)
    print(json.dumps({"activity_id":r.activity_id,"status":r.status,"target_time":r.target_time,
                      "tile_count":r.tile_count,"cells_updated":r.cells_updated,
                      "mapping":r.mapping_json,
                      "temperature_stats":(r.stats_json or {}).get("temperature_stats")},indent=2,default=str))
finally: db.close()
