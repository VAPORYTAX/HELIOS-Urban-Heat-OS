from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.contextforge.contracts import ContextBuildRequest
from app.contextforge.service import build_context_packet
from app.db.models_intelligence import IntelligenceRun
from app.intelligence.config import settings
from app.intelligence.contracts import IntelligenceQuery
from app.intelligence.fallback import deterministic_answer
from app.intelligence.firewall import validate_answer
from app.intelligence.gateway import chat, chat_native_fast, readiness
from app.intelligence.router import choose_model, choose_thinking, choose_profile

def _messages(packet: dict, user_query: str):
    prompts = packet.get("prompts", [])
    system = "\n\n".join(p["text"] for p in prompts if p.get("role") == "system")
    contract = """
Return exactly one JSON object with keys:
decision_status, headline, summary, recommended_actions, uncertainties,
evidence_refs, numeric_claims, requires_human_review.

STRICT HELIOS CONTRACT:
- numeric_claims keys MUST use canonical HELIOS paths exactly as supplied in context.
  Examples: optimizer.budget, optimizer.total_cost, optimizer.teu_reduction,
  optimizer.va_teu_reduction, optimizer.confidence, quality.health_score,
  phx-cell-04.teu, phx-cell-04.va_teu.
- Never invent friendly aliases such as budget_limit, total_portfolio_cost,
  teu_reduction, va_teu_reduction, portfolio_confidence, or health_score.
- uncertainties MUST always be a JSON array of strings, even when there is only one uncertainty.
- Every recommended_actions item MUST be an object containing only these allowed
  fields: cell_id, intervention_id, cost, estimated_teu_benefit,
  estimated_va_teu_benefit, confidence, priority, reason.
- Do not use action or rationale fields.
- Evidence refs MUST be copied exactly from HELIOS_CONTEXT_PACKET.evidence_refs.
- Counterfactual/modelled outputs are planning evidence, not causal proof.
- If HELIOS quality requires review, requires_human_review MUST be true and
  decision_status MUST NOT be recommend.
- Do not expose chain-of-thought or hidden reasoning.
"""
    return [
        {"role":"system","content":system + "\n\n" + contract},
        {"role":"user","content":"HELIOS_CONTEXT_PACKET:\n" + __import__("json").dumps(packet, default=str) + "\n\nUSER_QUERY:\n" + user_query},
    ]

def run_intelligence(db: Session, req: IntelligenceQuery):
    profile = choose_profile(req.task_type, req.mode, req.force_thinking)
    effective_budget = min(req.token_budget, profile["token_budget"])
    packet_row = build_context_packet(db, ContextBuildRequest(
        area_id=req.area_id,
        user_intent=req.query,
        mode=req.mode,
        task_type=req.task_type,
        token_budget=effective_budget,
        include_raw_evidence=profile["include_raw_evidence"],
    ))
    packet = packet_row.packet_json
    cfg = settings()
    thinking = profile["thinking"]
    model = choose_model(req.task_type, cfg)
    ready = readiness()

    raw = None
    latency = None
    fallback_used = False
    provider = "local_openai_compatible"
    status = "complete"

    if cfg["enabled"] and ready["reachable"]:
        try:
            if profile["name"] == "fast":
                raw, latency = chat_native_fast(
                    model_key="google/gemma-4-12b-qat",
                    messages=_messages(packet, req.query),
                    timeout=profile["timeout_seconds"],
                    max_output_tokens=profile["max_tokens"],
                    temperature=profile["temperature"],
                )
            else:
                raw, latency = chat(
                    model=model,
                    messages=_messages(packet, req.query),
                    thinking=thinking,
                    timeout=profile["timeout_seconds"],
                    max_tokens=profile["max_tokens"],
                    temperature=profile["temperature"],
                )
            answer, validation = validate_answer(raw, packet)
            if answer is None or not validation["valid"]:
                fallback_used = True
                raw = deterministic_answer(packet)
                answer, validation = validate_answer(raw, packet)
                status = "fallback"
        except Exception as exc:
            fallback_used = True
            raw = deterministic_answer(packet)
            answer, validation = validate_answer(raw, packet)
            validation["model_error"] = str(exc)
            status = "fallback"
    else:
        fallback_used = True
        raw = deterministic_answer(packet)
        answer, validation = validate_answer(raw, packet)
        validation["model_error"] = "local Gemma endpoint not reachable"
        status = "fallback"

    run = IntelligenceRun(
        context_packet_id=packet_row.id,
        area_id=req.area_id,
        provider=provider,
        model_name=model,
        mode=req.mode,
        thinking_enabled=thinking,
        status=status,
        request_json={**req.model_dump(), "inference_profile": profile["name"], "inference_transport": ("lmstudio_native" if profile["name"] == "fast" else "openai_compatible"), "effective_token_budget": effective_budget},
        response_json=raw,
        validation_json=validation,
        fallback_used=fallback_used,
        latency_ms=latency,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(run); db.commit(); db.refresh(run)
    return run
