from __future__ import annotations
from collections import defaultdict
from sqlalchemy import delete,desc,select
from geoalchemy2.shape import to_shape
from app.db.models_thermalway import ThermalWayOSMNode,ThermalWayOSMEdge,ThermalWayRouteRun
from app.db.models_thermalway_intel import ThermalWayCorridorScore
from app.db.models_exposure import Facility
from app.db.models_provider_ops import ProviderOperationalMetric
from app.thermalway.router import compare,route,PROFILE_MULT

HAVEN_HINTS={"hospital","clinic","library","community_centre","shelter","school","fire_station","police","station","public_building"}

def _facility_xy(f):
    for attr in ("geometry","geom","location"):
        if hasattr(f,attr) and getattr(f,attr) is not None:
            g=to_shape(getattr(f,attr)); return g.x,g.y
    return None

def safe_haven(db,origin_lon,origin_lat,profile="standard",area_id="phx-downtown",limit=12):
    facilities=db.execute(select(Facility)).scalars().all()
    candidates=[]
    for f in facilities:
        xy=_facility_xy(f)
        if not xy:continue
        raw=" ".join(str(getattr(f,a,"") or "") for a in ("facility_type","category","name","kind","amenity")).lower()
        if not any(h in raw for h in HAVEN_HINTS):continue
        try:
            r=route(db,origin_lon,origin_lat,xy[0],xy[1],"thermal_safe",profile,area_id)
        except RuntimeError:
            continue
        candidates.append((r.thermal_exposure_cost,r.duration_min,f,r))
        if len(candidates)>=limit: break
    if not candidates:
        raise RuntimeError("No routable safe-haven facility candidate found")
    candidates.sort(key=lambda x:(x[0],x[1]))
    tec,dur,f,r=candidates[0]
    return {
        "facility_id":str(getattr(f,"id","")),
        "facility_name":getattr(f,"name",None),
        "facility_type":getattr(f,"facility_type",None) or getattr(f,"category",None),
        "route_id":r.id,"distance_m":r.distance_m,"duration_min":dur,
        "thermal_exposure_cost":tec,"route":r.route_json,
        "truth_boundary":"Facility is observed OSM context; route is real OSM; thermal cost is modelled."
    }

def route_time_scenarios(db,origin_lon,origin_lat,dest_lon,dest_lat,profile="standard",area_id="phx-downtown"):
    fast,safe=compare(db,origin_lon,origin_lat,dest_lon,dest_lat,profile,area_id)
    # Stored thermal provider state is one timestamp. We do NOT invent hourly forecasts.
    return {
        "current":{"fastest_route_id":fast.id,"thermal_safe_route_id":safe.id,
                   "fastest_tec":fast.thermal_exposure_cost,"thermal_safe_tec":safe.thermal_exposure_cost,
                   "thermal_cost_saved":fast.thermal_exposure_cost-safe.thermal_exposure_cost,
                   "extra_minutes":safe.duration_min-fast.duration_min},
        "departure_time_optimizer":{
            "status":"provider_forecast_required",
            "reason":"Current provider field supports now-routing only; no future hourly FortyGuard field is stored.",
            "synthetic_hourly_forecast_used":False
        }
    }

def exposure_budget(db,origin_lon,origin_lat,dest_lon,dest_lat,profile="standard",budget=None,area_id="phx-downtown"):
    fast,safe=compare(db,origin_lon,origin_lat,dest_lon,dest_lat,profile,area_id)
    if budget is None: budget=fast.thermal_exposure_cost
    return {
        "budget":budget,
        "fastest":{"route_id":fast.id,"tec":fast.thermal_exposure_cost,"within_budget":fast.thermal_exposure_cost<=budget},
        "thermal_safe":{"route_id":safe.id,"tec":safe.thermal_exposure_cost,"within_budget":safe.thermal_exposure_cost<=budget},
        "recommended":"thermal_safe" if safe.thermal_exposure_cost<=budget else "no_route_within_budget",
        "saved_vs_fastest":fast.thermal_exposure_cost-safe.thermal_exposure_cost
    }

def rebuild_corridor_intelligence(db,area_id="phx-downtown"):
    routes=db.execute(select(ThermalWayRouteRun).where(ThermalWayRouteRun.area_id==area_id)).scalars().all()
    if not routes: raise RuntimeError("No ThermalWay route evidence")
    agg=defaultdict(lambda:{"tec":0.0,"vtec":0.0,"freq":0,"temps":[]})
    for r in routes:
        mult=PROFILE_MULT.get(r.traveler_profile,1.0)
        for fp in (r.route_json or {}).get("fingerprint",[]):
            eid=fp.get("edge_id")
            if not eid:continue
            tec=float(fp.get("thermal_exposure_cost") or 0)
            a=agg[eid];a["tec"]+=tec;a["vtec"]+=tec*mult;a["freq"]+=1
            if fp.get("temperature_c") is not None:a["temps"].append(float(fp["temperature_c"]))
    if not agg:raise RuntimeError("No route fingerprint evidence")

    db.execute(delete(ThermalWayCorridorScore).where(ThermalWayCorridorScore.area_id==area_id))
    maxscore=max((v["vtec"]*(1+__import__("math").log1p(v["freq"])) for v in agg.values()),default=1)
    rows=[]
    for eid,v in agg.items():
        raw=v["vtec"]*(1+__import__("math").log1p(v["freq"]))
        priority=raw/maxscore if maxscore else 0
        temp=sum(v["temps"])/len(v["temps"]) if v["temps"] else None
        intervention="shade_structure" if priority>=.70 else ("tree_canopy" if priority>=.40 else "cool_pavement")
        row=ThermalWayCorridorScore(
            area_id=area_id,edge_id=eid,thermal_cost=v["tec"],vulnerable_thermal_cost=v["vtec"],
            route_frequency=v["freq"],investment_priority=priority,recommended_intervention=intervention,
            evidence_json={"route_evidence_count":v["freq"],"mean_provider_temperature_c":temp,
                           "truth_category":"derived_from_real_routes_and_provider_thermal",
                           "causal_claim":False})
        db.add(row);rows.append(row)
    db.commit()
    rows.sort(key=lambda r:r.investment_priority,reverse=True)
    return rows
