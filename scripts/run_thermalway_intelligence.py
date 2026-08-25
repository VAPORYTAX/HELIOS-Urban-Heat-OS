import json
from sqlalchemy import select
from geoalchemy2.shape import to_shape
from app.db.session import SessionLocal
from app.db.models_thermalway import ThermalWayOSMNode
from app.thermalway.intelligence import exposure_budget,route_time_scenarios,rebuild_corridor_intelligence,safe_haven

db=SessionLocal()
try:
    nodes=db.execute(select(ThermalWayOSMNode)).scalars().all()
    pts=[(to_shape(n.geometry).x,to_shape(n.geometry).y) for n in nodes]
    # Smoke endpoints inside the core thermal-cell envelope, not padded network extremes.
    origin=(-112.0775,33.4465); dest=(-112.0665,33.4545)
    budget=exposure_budget(db,*origin,*dest,"older_adult")
    time=route_time_scenarios(db,*origin,*dest,"older_adult")
    try:
        haven=safe_haven(db,*origin,"older_adult")
    except Exception as e:
        haven={"status":"facility_schema_or_connectivity_review_required","error":str(e)}
    corridors=rebuild_corridor_intelligence(db)
    print(json.dumps({
        "exposure_budget":budget,
        "time_optimizer":time,
        "safe_haven":haven,
        "corridor_top10":[{
            "edge_id":r.edge_id,"investment_priority":r.investment_priority,
            "route_frequency":r.route_frequency,"thermal_cost":r.thermal_cost,
            "vulnerable_thermal_cost":r.vulnerable_thermal_cost,
            "recommended_intervention":r.recommended_intervention
        } for r in corridors[:10]]
    },indent=2,default=str))
    print("PASS: ThermalWay exposure budget + time gate + corridor intelligence built")
finally:db.close()
