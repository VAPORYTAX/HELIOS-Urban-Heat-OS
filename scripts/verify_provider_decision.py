from sqlalchemy import desc,select
from app.db.session import SessionLocal
from app.db.models_provider_decision import ProviderOptimizerRun,ProviderAgentDecision,ProviderInterventionCandidate
from app.db.models_context import ContextPacket
db=SessionLocal()
try:
    opt=db.execute(select(ProviderOptimizerRun).where(ProviderOptimizerRun.area_id=="phx-downtown").order_by(desc(ProviderOptimizerRun.created_at)).limit(1)).scalar_one()
    assert opt.total_cost<=opt.budget+1e-9
    assert len(opt.selected_json)>0
    assert opt.teu_reduction>=0 and opt.va_teu_reduction>=0
    agent=db.execute(select(ProviderAgentDecision).where(ProviderAgentDecision.optimizer_run_id==opt.id).order_by(desc(ProviderAgentDecision.created_at)).limit(1)).scalar_one()
    assert agent.requires_human_review is True
    cp=db.execute(select(ContextPacket).where(ContextPacket.area_id=="phx-downtown").order_by(desc(ContextPacket.created_at)).limit(1)).scalar_one()
    assert cp.packet_json["state"]["optimizer"]["id"]==opt.id
    assert cp.packet_json["state"]["optimizer_status"]["status"]=="rebuilt_provider_native"
    kinds={x["kind"] for x in cp.packet_json["evidence_refs"]}
    assert "optimizer" in kinds and "agent_decision" in kinds
    print("PASS: provider optimizer is budget-feasible")
    print("PASS: governed agent decision requires human review")
    print("PASS: ContextForge references rebuilt optimizer + agent decision")
finally:db.close()
