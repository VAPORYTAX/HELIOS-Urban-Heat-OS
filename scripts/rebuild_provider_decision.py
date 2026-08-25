import json
from app.db.session import SessionLocal
from app.provider_decision.service import rebuild_decision_stack
db=SessionLocal()
try:
    opt,agent=rebuild_decision_stack(db)
    print(json.dumps({
        "optimizer_run_id":opt.id,"status":opt.status,"budget":opt.budget,
        "total_cost":opt.total_cost,"selected_count":len(opt.selected_json),
        "teu_reduction":opt.teu_reduction,"va_teu_reduction":opt.va_teu_reduction,
        "confidence":opt.confidence,"agent_decision_id":agent.id,
        "agent_status":agent.status,"human_review":agent.requires_human_review
    },indent=2))
    print("PASS: provider-native twin + optimizer + agents rebuilt")
finally: db.close()
