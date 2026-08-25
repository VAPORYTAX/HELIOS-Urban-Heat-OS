from fastapi import APIRouter,Depends,Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.thermalway.router import compare,route
router=APIRouter(prefix="/thermalway",tags=["thermalway"])


def serialize(r):
    return {"id":r.id,"mode":r.mode,"profile":r.traveler_profile,"distance_m":r.distance_m,
            "duration_min":r.duration_min,"thermal_exposure_cost":r.thermal_exposure_cost,
            "confidence":r.confidence,"truth_category":r.truth_category,"route":r.route_json}


@router.get("/compare")
def compare_routes(
    origin_lon:float,origin_lat:float,dest_lon:float,dest_lat:float,
    profile:str=Query("standard",pattern="^(standard|child|older_adult|outdoor_worker|mobility_limited)$"),
    db:Session=Depends(get_db)
):
    fast,safe=compare(db,origin_lon,origin_lat,dest_lon,dest_lat,profile)
    return {"fastest":serialize(fast),"thermal_safe":serialize(safe),
            "exposure_budget":{"thermal_cost_saved":max(0,fast.thermal_exposure_cost-safe.thermal_exposure_cost),
                               "extra_minutes":max(0,safe.duration_min-fast.duration_min)}}


@router.get("/route")
def route_mode(
    origin_lon:float,origin_lat:float,dest_lon:float,dest_lat:float,
    mode:str=Query("thermal_safe",pattern="^(fastest|cool|warm|thermal_safe)$"),
    profile:str=Query("standard",pattern="^(standard|child|older_adult|outdoor_worker|mobility_limited)$"),
    db:Session=Depends(get_db)
):
    r=route(db,origin_lon,origin_lat,dest_lon,dest_lat,mode,profile)
    body=serialize(r)
    body["mode_contract"]={
        "fastest":"minimize travel time/distance cost",
        "cool":"minimize cumulative modeled heat exposure",
        "warm":"minimize cumulative modeled cold exposure",
        "thermal_safe":"minimize modeled thermal stress",
    }[mode]
    body["truth_boundary"]="Route geometry uses the real OSM graph; thermal cost is modeled from available provider thermal state and route context, not medical risk."
    return body


@router.get("/modes")
def modes():
    return {
        "modes":[
            {"id":"fastest","label":"Fastest","objective":"travel time","algorithm":"astar"},
            {"id":"cool","label":"Cool Route","objective":"modeled cumulative heat exposure","algorithm":"dijkstra"},
            {"id":"warm","label":"Warm Route","objective":"modeled cumulative cold exposure","algorithm":"dijkstra"},
            {"id":"thermal_safe","label":"Thermal-Safe Route","objective":"modeled thermal stress","algorithm":"dijkstra"},
        ],
        "current_field":"provider now-state",
        "future_hourly_forecast_required_for_departure_optimization":True,
        "synthetic_hourly_forecast_used":False,
        "truth_category":"real_osm_provider_thermal_modelled_cost",
    }
