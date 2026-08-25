from sqlalchemy import desc,select
from app.db.models_provider_decision import ProviderOptimizerRun,ProviderAgentDecision

def inject_provider_decision(db,packet,area_id):
    opt=db.execute(select(ProviderOptimizerRun).where(ProviderOptimizerRun.area_id==area_id).order_by(desc(ProviderOptimizerRun.created_at)).limit(1)).scalar_one_or_none()
    if not opt:return packet
    agent=db.execute(select(ProviderAgentDecision).where(ProviderAgentDecision.optimizer_run_id==opt.id).order_by(desc(ProviderAgentDecision.created_at)).limit(1)).scalar_one_or_none()
    packet.setdefault("state",{})
    packet["state"]["optimizer"]={
        "id":opt.id,"status":opt.status,"budget":opt.budget,"objective":opt.objective,
        "total_cost":opt.total_cost,"teu_reduction":opt.teu_reduction,
        "va_teu_reduction":opt.va_teu_reduction,"confidence":opt.confidence,
        "selected":opt.selected_json,"truth_category":"modelled_provider_decision"
    }
    packet["state"]["optimizer_status"]={"status":"rebuilt_provider_native","requires_rebuild":False}
    if agent:
        packet["state"]["agent_decision"]={
            "id":agent.id,"status":agent.status,"confidence":agent.confidence,
            "requires_human_review":agent.requires_human_review,
            "actions":agent.agent_actions_json,"truth_category":"governed_modelled"
        }
    refs=packet.setdefault("evidence_refs",[])
    refs=[x for x in refs if x.get("kind") not in {"optimizer","agent_decision"}]
    refs.insert(0,{"kind":"optimizer","ref":opt.id,"truth_category":"modelled_provider_decision","confidence":opt.confidence,"utility_score":0.95*opt.confidence})
    if agent:
        refs.insert(0,{"kind":"agent_decision","ref":agent.id,"truth_category":"governed_modelled","confidence":agent.confidence,"utility_score":0.96*agent.confidence})
    packet["evidence_refs"]=refs
    return packet
