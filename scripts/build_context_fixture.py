import json
from app.contextforge.contracts import ContextBuildRequest
from app.contextforge.service import build_context_packet
from app.db.session import SessionLocal
db=SessionLocal()
try:
    row=build_context_packet(db,ContextBuildRequest(
        area_id="phx-downtown",
        user_intent="Given a $100,000 planning budget, prioritize interventions that reduce heat burden while protecting vulnerable residents.",
        mode="investment",task_type="portfolio_optimization",token_budget=24000))
    print(json.dumps({"id":row.id,"context_hash":row.context_hash,"prompt_bundle_version":row.prompt_bundle_version,
                      "status":row.status,"token_budget":row.token_budget,"estimated_tokens":row.estimated_tokens,
                      "task":row.packet_json["task"],"quality":row.packet_json["state"]["quality"],
                      "cells":row.packet_json["state"]["cells"],"evidence_refs":row.packet_json["evidence_refs"],
                      "prompt_count":len(row.packet_json["prompts"])},indent=2))
finally:db.close()
