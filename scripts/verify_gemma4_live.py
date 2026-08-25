from sqlalchemy import desc,select
from app.db.session import SessionLocal
from app.db.models_intelligence import IntelligenceRun
db=SessionLocal()
try:
    r=db.execute(select(IntelligenceRun).order_by(desc(IntelligenceRun.created_at)).limit(1)).scalar_one()
    assert r.model_name=="helios-gemma4"
    assert r.provider=="local_openai_compatible"
    assert r.fallback_used is False
    assert r.status=="complete"
    assert r.validation_json.get("valid") is True
    assert r.response_json.get("requires_human_review") is True
    print("PASS: latest intelligence run is helios-gemma4")
    print("PASS: provider local_openai_compatible")
    print("PASS: fallback false")
    print("PASS: validation valid")
    print("PASS: human review true")
finally:
    db.close()
