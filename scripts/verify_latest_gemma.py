from sqlalchemy import desc, select
from app.db.session import SessionLocal
from app.db.models_intelligence import IntelligenceRun

db = SessionLocal()
try:
    r = db.execute(
        select(IntelligenceRun).order_by(desc(IntelligenceRun.created_at)).limit(1)
    ).scalar_one()
    print("LATEST_RUN", r.id)
    print("MODEL", r.model_name)
    print("STATUS", r.status)
    print("FALLBACK_USED", r.fallback_used)
    print("VALID", r.validation_json.get("valid") if isinstance(r.validation_json, dict) else None)
    print("HUMAN_REVIEW", r.response_json.get("requires_human_review") if isinstance(r.response_json, dict) else None)
    assert r.model_name == "helios-gemma4"
    assert r.fallback_used is False
    assert r.status == "complete"
    assert isinstance(r.validation_json, dict) and r.validation_json.get("valid") is True
    assert isinstance(r.response_json, dict) and r.response_json.get("requires_human_review") is True
    print("PASS: persisted genuine Gemma-backed HELIOS decision")
finally:
    db.close()
