def deterministic_answer(packet: dict) -> dict:
    quality = packet.get("state", {}).get("quality") or {}
    opt = packet.get("state", {}).get("optimizer") or {}
    actions = opt.get("actions") or []
    review = bool(quality.get("requires_human_review", True))
    return {
        "decision_status": "review_required" if review else "recommend",
        "headline": (
            "HELIOS portfolio requires human review before operational use."
            if review else "HELIOS portfolio is recommended under the stated constraints."
        ),
        "summary": (
            "This response was generated deterministically from HELIOS verified engines because "
            "the local language model was unavailable or failed validation."
        ),
        "recommended_actions": actions,
        "uncertainties": [
            "Live FortyGuard-derived provider observations are available; review recency, confidence, and provider quality before operational use."
        ] if review else [],
        "evidence_refs": [x["ref"] for x in packet.get("evidence_refs", [])[:10]],
        "numeric_claims": {},
        "requires_human_review": review,
    }
