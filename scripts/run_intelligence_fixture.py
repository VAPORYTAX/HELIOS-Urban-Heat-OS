import json
from app.db.session import SessionLocal
from app.intelligence.contracts import IntelligenceQuery
from app.intelligence.gateway import readiness
from app.intelligence.service import run_intelligence

print(json.dumps({"gemma_readiness": readiness()}, indent=2))
db = SessionLocal()
try:
    run = run_intelligence(db, IntelligenceQuery(
        area_id="phx-downtown",
        query="Given the current HELIOS evidence and a $100,000 budget, what should Phoenix prioritize and why?",
        mode="investment",
        task_type="portfolio_optimization",
        token_budget=24000,
    ))
    print(json.dumps({
        "run_id": run.id,
        "model": run.model_name,
        "thinking_enabled": run.thinking_enabled,
        "status": run.status,
        "fallback_used": run.fallback_used,
        "latency_ms": run.latency_ms,
        "answer": run.response_json,
        "validation": run.validation_json,
    }, indent=2))
finally:
    db.close()
