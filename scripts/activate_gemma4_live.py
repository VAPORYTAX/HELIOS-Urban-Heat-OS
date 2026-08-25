import json, os
from sqlalchemy import desc, select
from app.db.session import SessionLocal
from app.intelligence.gateway import readiness
from app.intelligence.service import run_intelligence
from app.intelligence.contracts import IntelligenceQuery
from app.db.models_intelligence import IntelligenceRun

ready=readiness()
print("=== GEMMA READINESS ===")
print(json.dumps(ready,indent=2,default=str))

assert ready["reachable"] is True, "LM Studio endpoint not reachable"
assert "helios-gemma4" in ready.get("available_models",[]), "helios-gemma4 not exposed by LM Studio"
assert ready["model"]=="helios-gemma4", f"Primary model mismatch: {ready['model']}"
assert ready["fallback_model"]=="helios-gemma4", f"Fallback route mismatch: {ready['fallback_model']}"

db=SessionLocal()
try:
    # Use the project's own fixture contract by importing its schema dynamically.
    fields=IntelligenceQuery.model_fields
    payload={}
    if "query" in fields:
        payload["query"]="Assess the current provider-backed heat intervention portfolio for phx-downtown. Use only HELIOS evidence. State uncertainties, do not make causal claims, and require human review."
    if "task_type" in fields:
        payload["task_type"]="portfolio_optimization"
    if "force_thinking" in fields:
        payload["force_thinking"] = False
    if "mode" in fields:
        payload["mode"]="investment"
    if "area_id" in fields:
        payload["area_id"]="phx-downtown"
    if "thinking" in fields:
        payload["thinking"]=False
    if "thinking_enabled" in fields:
        payload["thinking_enabled"]=False

    # Fill only fields that have no default and are recognizable from their annotations/names.
    for name,f in fields.items():
        if name in payload:
            continue
        if not f.is_required():
            continue
        if name=="user_intent":
            payload[name]=payload.get("query","Assess provider-backed HELIOS decision evidence.")
        elif name=="budget":
            payload[name]=100000.0
        elif name=="task":
            payload[name]="portfolio_optimization"
        else:
            raise RuntimeError(f"Unresolved required IntelligenceQuery field: {name}")

    req=IntelligenceQuery(**payload)
    run=run_intelligence(db,req)
    db.refresh(run)

    result={
        "id":run.id,
        "provider":run.provider,
        "model":run.model_name,
        "mode":run.mode,
        "thinking_enabled":run.thinking_enabled,
        "status":run.status,
        "fallback_used":run.fallback_used,
        "latency_ms":run.latency_ms,
        "answer":run.response_json,
        "validation":run.validation_json,
    }
    print("=== LIVE GEMMA DECISION ===")
    print(json.dumps(result,indent=2,default=str))

    assert run.model_name=="helios-gemma4", f"Unexpected model {run.model_name}"
    assert run.fallback_used is False, "Gemma run fell back; inspect validation/model_error"
    assert run.status=="complete", f"Expected complete, got {run.status}"
    assert isinstance(run.validation_json,dict) and run.validation_json.get("valid") is True, "Validation failed"
    assert isinstance(run.response_json,dict), "Structured answer missing"
    assert run.response_json.get("requires_human_review") is True, "Human-review requirement missing"
    assert run.response_json.get("decision_status")!="recommend", "Review-gated decision must not be promoted to recommend"

    print("PASS: genuine Gemma-backed HELIOS decision")
    print("PASS: fallback_used = false")
    print("PASS: structured validation = true")
    print("PASS: human review retained")
finally:
    db.close()

