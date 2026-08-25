import json
from sqlalchemy import select
from geoalchemy2.shape import to_shape
from app.db.session import SessionLocal
from app.db.models_thermalway import ThermalWayOSMNode
from app.thermalway.osm_ingest import ingest_osm_network
from app.thermalway.router import compare

db=SessionLocal()
try:
    ing=ingest_osm_network(db)
    nodes=db.execute(select(ThermalWayOSMNode)).scalars().all()
    pts=[(n.osm_node_id,to_shape(n.geometry).x,to_shape(n.geometry).y) for n in nodes]
    # Choose a real-network diagonal for deterministic smoke routing.
    west=min(pts,key=lambda p:p[1]+p[2]);east=max(pts,key=lambda p:p[1]+p[2])
    fast,safe=compare(db,west[1],west[2],east[1],east[2],"older_adult")
    print(json.dumps({"ingest":ing,"smoke":{
      "origin":[west[1],west[2]],"destination":[east[1],east[2]],
      "fastest":{"distance_m":fast.distance_m,"duration_min":fast.duration_min,"tec":fast.thermal_exposure_cost},
      "thermal_safe":{"distance_m":safe.distance_m,"duration_min":safe.duration_min,"tec":safe.thermal_exposure_cost},
      "profile":"older_adult"
    }},indent=2,default=str))
    print("PASS: real OSM ThermalWay network + comparison route built")
finally:db.close()
