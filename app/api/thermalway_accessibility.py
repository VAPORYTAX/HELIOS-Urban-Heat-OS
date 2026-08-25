from fastapi import APIRouter,Depends,Query
from sqlalchemy import desc,select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models_thermalway_access import ThermalWayAccessibilityScore,ThermalWayCriticalJourney
from app.thermalway.pareto import pareto_routes
router=APIRouter(prefix="/thermalway",tags=["thermalway-accessibility"])
@router.get("/pareto")
def pareto(origin_lon:float,origin_lat:float,dest_lon:float,dest_lat:float,profile:str="standard",k:int=Query(5,ge=2,le=5),db:Session=Depends(get_db)):
    return pareto_routes(db,origin_lon,origin_lat,dest_lon,dest_lat,profile,k=k)
@router.get("/accessibility")
def access(area_id:str="phx-downtown",db:Session=Depends(get_db)):
    rows=db.execute(select(ThermalWayAccessibilityScore).where(ThermalWayAccessibilityScore.area_id==area_id).order_by(desc(ThermalWayAccessibilityScore.created_at))).scalars().all()
    latest={}
    for r in rows: latest.setdefault(r.cell_id,r)
    return [{"cell_id":r.cell_id,"profile":r.traveler_profile,"score":r.accessibility_score,"best_duration_min":r.best_duration_min,"best_tec":r.best_tec,"best_facility":r.best_facility_json} for r in latest.values()]
@router.get("/critical-journeys")
def journeys(area_id:str="phx-downtown",db:Session=Depends(get_db)):
    rows=db.execute(select(ThermalWayCriticalJourney).where(ThermalWayCriticalJourney.area_id==area_id).order_by(desc(ThermalWayCriticalJourney.created_at))).scalars().all()
    return [{"type":r.journey_type,"cell":r.origin_cell_id,"profile":r.traveler_profile,"facility":r.facility_json,"fastest":r.fastest_json,"thermal_safe":r.thermal_safe_json,"saved":r.thermal_cost_saved,"extra_minutes":r.extra_minutes,"protection_score":r.protection_score} for r in rows[:40]]
