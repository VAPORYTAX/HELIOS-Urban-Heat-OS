from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models_thermalway_access import ThermalWayAccessibilityScore,ThermalWayCriticalJourney
db=SessionLocal()
try:
    a=db.execute(select(ThermalWayAccessibilityScore)).scalars().all(); j=db.execute(select(ThermalWayCriticalJourney)).scalars().all()
    assert len(a)>=4 and all(0<=x.accessibility_score<=100 for x in a)
    assert len(j)>=4 and all(x.protection_score>=0 for x in j)
    print("PASS: accessibility rows",len(a)); print("PASS: critical journeys",len(j))
finally: db.close()
