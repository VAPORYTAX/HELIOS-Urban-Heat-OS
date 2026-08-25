import json
from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models_fortyguard_checkpoint import FortyGuardHistoryCheckpoint
from app.db.models_provider_history import ProviderThermalBaseline

db=SessionLocal()
try:
    ck=db.execute(select(FortyGuardHistoryCheckpoint)).scalars().all()
    bl=db.execute(select(ProviderThermalBaseline).where(ProviderThermalBaseline.area_id=="phx-downtown")).scalars().all()
    assert len(bl)>=4, f"expected >=4 provider baseline rows, got {len(bl)}"
    states={}
    for r in ck: states[r.state]=states.get(r.state,0)+1
    legacy=[r for r in ck if r.activity_id=="73ff7877-056f-4410-87e3-0d508c2a947b"]
    assert legacy and legacy[0].state=="COMPLETE_NO_DATA"
    print(json.dumps({"baseline_rows":len(bl),"checkpoint_state_counts":states,
                      "legacy_no_data_checkpointed":True},indent=2))
    print("PASS: provider history checkpoints + baselines verified")
finally:
    db.close()
