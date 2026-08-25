from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.thermalway.router import compare
router=APIRouter(prefix="/thermalway",tags=["thermalway"])

@router.get("/compare")
def compare_routes(
    origin_lon:float,origin_lat:float,dest_lon:float,dest_lat:float,
    profile:str=Query("standard",pattern="^(standard|child|older_adult|outdoor_worker|mobility_limited)$"),
    db:Session=Depends(get_db)
):
    fast,safe=compare(db,origin_lon,origin_lat,dest_lon,dest_lat,profile)
    def x(r):return {"id":r.id,"mode":r.mode,"profile":r.traveler_profile,"distance_m":r.distance_m,
                     "duration_min":r.duration_min,"thermal_exposure_cost":r.thermal_exposure_cost,
                     "confidence":r.confidence,"truth_category":r.truth_category,"route":r.route_json}
    return {"fastest":x(fast),"thermal_safe":x(safe),
            "exposure_budget":{"thermal_cost_saved":max(0,fast.thermal_exposure_cost-safe.thermal_exposure_cost),
                               "extra_minutes":max(0,safe.duration_min-fast.duration_min)}}
