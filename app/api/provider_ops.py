from fastapi import APIRouter,Depends
from sqlalchemy import desc,select
from sqlalchemy.orm import Session
from app.db.models_provider_ops import ProviderOperationalMetric
from app.db.session import get_db
router=APIRouter(prefix="/provider-ops",tags=["provider-operational"])
@router.get("/metrics")
def metrics(area_id:str="phx-downtown",db:Session=Depends(get_db)):
    rows=db.execute(select(ProviderOperationalMetric).where(ProviderOperationalMetric.area_id==area_id).order_by(desc(ProviderOperationalMetric.created_at))).scalars().all()
    latest={}
    for r in rows: latest.setdefault(r.cell_id,r)
    return [{
        "cell_id":r.cell_id,"current_c":r.current_c,"baseline_mean_c":r.baseline_mean_c,
        "anomaly_c":r.anomaly_c,"z_score":r.z_score,"persistence_hours":r.persistence_hours,
        "exceedance_hours":r.exceedance_hours,"hazard_index":r.hazard_index,"severity":r.severity,
        "population":r.population,"vulnerability_index":r.vulnerability_index,"teu":r.teu,
        "va_teu":r.va_teu,"confidence":r.confidence,"truth_category":r.truth_category,
        "model_version":r.model_version,"evidence":r.evidence_json
    } for r in latest.values()]
