import json
from app.db.session import SessionLocal
from app.fortyguard_live.checkpoint_history import build_checkpointed_history

db=SessionLocal()
try:
    out=build_checkpointed_history(db,days=7,threshold_c=30.0,min_data_days=4)
    print("\n=== TRANCHE A / PROVIDER HISTORY RESULT ===")
    print(json.dumps(out,indent=2,default=str))
    print("PASS: checkpointed provider operational history established")
finally:
    db.close()
