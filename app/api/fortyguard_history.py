from fastapi import APIRouter,Depends
from sqlalchemy import desc,select
from sqlalchemy.orm import Session
from app.db.models_provider_history import ProviderThermalBaseline,ProviderThermalStress
from app.db.session import get_db
router=APIRouter(prefix="/fortyguard/history",tags=["fortyguard-history"])

@router.get("/baselines")
def baselines(area_id:str,db:Session=Depends(get_db)):
    rows=db.execute(select(ProviderThermalBaseline).where(ProviderThermalBaseline.area_id==area_id).order_by(desc(ProviderThermalBaseline.created_at))).scalars().all()
    return [{"cell_id":r.cell_id,"local_hour":r.local_hour,"sample_days":r.sample_days,
             "mean_c":r.mean_c,"median_c":r.median_c,"std_c":r.std_c,"current_c":r.current_c,
             "anomaly_c":r.anomaly_c,"z_score":r.z_score,"confidence":r.confidence,
             "truth_category":r.truth_category,"created_at":r.created_at} for r in rows[:20]]

@router.get("/stress")
def stress(area_id:str,db:Session=Depends(get_db)):
    rows=db.execute(select(ProviderThermalStress).where(ProviderThermalStress.area_id==area_id).order_by(desc(ProviderThermalStress.created_at))).scalars().all()
    return [{"cell_id":r.cell_id,"period_date":r.period_date,"threshold_c":r.threshold_c,
             "persistence_hours":r.persistence_hours,"exceedance_hours":r.exceedance_hours,
             "confidence":r.confidence,"truth_category":r.truth_category,"created_at":r.created_at} for r in rows[:20]]
