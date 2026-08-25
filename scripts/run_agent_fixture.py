import json
from app.agents.contracts import AgentDecisionRequest
from app.agents.service import run_agents
from app.db.session import SessionLocal

db=SessionLocal()
try:
    run,rec=run_agents(db,AgentDecisionRequest(
        area_id="phx-downtown",
        mode="planning",
        min_recommendation_confidence=0.70,
        require_real_data_for_operational=True,
    ))
    print(json.dumps({
        "run_id":run.id,
        "status":run.status,
        "mode":run.mode,
        "decision_status":rec.decision_status,
        "headline":rec.headline,
        "confidence":rec.confidence,
        "requires_human_review":rec.requires_human_review,
        "skeptic_findings":rec.skeptic_findings_json,
        "evidence_summary":rec.evidence_summary_json,
        "executive_summary":rec.executive_summary_json,
        "recommended_action_count":len(rec.recommended_actions_json.get("actions",[])),
    },indent=2))
finally:
    db.close()
