import json
from app.db.session import SessionLocal
from app.provider_ops.service import rebuild_provider_metrics
db=SessionLocal()
try:
    rows=rebuild_provider_metrics(db)
    print(json.dumps([{
        "cell_id":r.cell_id,"current_c":r.current_c,"baseline_mean_c":r.baseline_mean_c,
        "anomaly_c":r.anomaly_c,"z_score":r.z_score,"persistence_hours":r.persistence_hours,
        "exceedance_hours":r.exceedance_hours,"hazard_index":r.hazard_index,"severity":r.severity,
        "population":r.population,"teu":r.teu,"va_teu":r.va_teu,"confidence":r.confidence
    } for r in rows],indent=2))
    print("PASS: provider operational hazard + TEU/VA-TEU rebuilt")
finally:db.close()
