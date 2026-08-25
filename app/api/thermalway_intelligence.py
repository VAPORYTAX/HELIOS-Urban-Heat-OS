from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.thermalway.intelligence import safe_haven,route_time_scenarios,exposure_budget
router=APIRouter(prefix="/thermalway",tags=["thermalway-intelligence"])

@router.get("/safe-haven")
def safe_haven_route(origin_lon:float,origin_lat:float,profile:str="standard",db:Session=Depends(get_db)):
    return safe_haven(db,origin_lon,origin_lat,profile)

@router.get("/time-optimizer")
def time_optimizer(origin_lon:float,origin_lat:float,dest_lon:float,dest_lat:float,profile:str="standard",db:Session=Depends(get_db)):
    return route_time_scenarios(db,origin_lon,origin_lat,dest_lon,dest_lat,profile)

@router.get("/exposure-budget")
def budget(origin_lon:float,origin_lat:float,dest_lon:float,dest_lat:float,profile:str="standard",thermal_budget:float|None=None,db:Session=Depends(get_db)):
    return exposure_budget(db,origin_lon,origin_lat,dest_lon,dest_lat,profile,thermal_budget)
