from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models_thermalway import ThermalWayOSMNode,ThermalWayOSMEdge,ThermalWayRouteRun
db=SessionLocal()
try:
    nc=len(db.execute(select(ThermalWayOSMNode)).scalars().all())
    ec=len(db.execute(select(ThermalWayOSMEdge)).scalars().all())
    routes=db.execute(select(ThermalWayRouteRun)).scalars().all()
    assert nc>=10 and ec>=10
    assert any(r.mode=="fastest" for r in routes)
    assert any(r.mode=="thermal_safe" for r in routes)
    assert all(r.truth_category=="real_osm_provider_thermal_modelled_cost" for r in routes[-2:])
    print("PASS: real OSM nodes",nc)
    print("PASS: real OSM routing edges",ec)
    print("PASS: fastest + thermal-safe route persisted")
    print("PASS: route truth boundary explicit")
finally:db.close()
