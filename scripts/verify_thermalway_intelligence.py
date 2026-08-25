from sqlalchemy import desc,select
from app.db.session import SessionLocal
from app.db.models_thermalway import ThermalWayRouteRun
from app.db.models_thermalway_intel import ThermalWayCorridorScore
db=SessionLocal()
try:
    rs=db.execute(select(ThermalWayRouteRun).order_by(desc(ThermalWayRouteRun.created_at))).scalars().all()
    f=next(r for r in rs if r.mode=="fastest")
    s=next(r for r in rs if r.mode=="thermal_safe")
    assert f.thermal_exposure_cost>0, "fastest TEC must be computed, not zeroed"
    assert s.thermal_exposure_cost>0
    cs=db.execute(select(ThermalWayCorridorScore)).scalars().all()
    assert len(cs)>0
    assert all(0<=c.investment_priority<=1 for c in cs)
    print("PASS: fastest route TEC is computed")
    print("PASS: thermal-safe route TEC is computed")
    print("PASS: corridor investment intelligence persisted",len(cs),"edges")
finally:db.close()
