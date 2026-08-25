import json
from app.db.session import SessionLocal
from app.thermalway.network_audit import audit_real_network

db = SessionLocal()
try:
    row = audit_real_network(db)
    print(json.dumps({
        "audit_id": row.id,
        "status": row.status,
        "real_osm_network_proven": row.real_osm_network_proven,
        "source_table": row.source_table,
        "geometry_column": row.geometry_column,
        "line_feature_count": row.line_feature_count,
        "candidate_tables": row.candidate_tables_json,
        "notes": row.notes_json,
    }, indent=2, default=str))
    print("THERMALWAY_NETWORK_STATUS:", row.status)
finally:
    db.close()
