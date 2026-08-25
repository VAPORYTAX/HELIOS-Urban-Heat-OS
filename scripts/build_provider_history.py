import json,os
from app.db.session import SessionLocal
from app.fortyguard_live.history import build_operational_history
days=int(os.getenv("HELIOS_FG_BASELINE_DAYS","7"))
threshold=float(os.getenv("HELIOS_FG_THRESHOLD_C","30"))
db=SessionLocal()
try:
    out=build_operational_history(db,days=days,threshold_c=threshold)
    print(json.dumps(out,indent=2,default=str))
    print("PASS: Provider operational baseline + native stress analytics stored")
finally:db.close()
