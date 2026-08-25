from __future__ import annotations
from app.intelligence.contracts import IntelligenceAnswer

ALLOWED_ACTION_KEYS = {
    "cell_id","intervention_id","cost","estimated_teu_benefit",
    "estimated_va_teu_benefit","confidence","priority","reason"
}

def collect_authoritative_numbers(packet: dict) -> dict[str, float]:
    nums = {}
    for cell in packet.get("state", {}).get("cells", []):
        cid = cell.get("cell_id")
        if not cid:
            continue
        for key in ("teu","va_teu","hazard_index","exposure_index","vulnerability_index","confidence"):
            v = cell.get(key)
            if isinstance(v, (int,float)):
                nums[f"{cid}.{key}"] = float(v)

    opt = packet.get("state", {}).get("optimizer") or {}
    for key in ("budget","total_cost","selected_count"):
        v = opt.get(key)
        if isinstance(v,(int,float)):
            nums[f"optimizer.{key}"] = float(v)
    for key in ("teu_reduction","teu_reduction_pct","va_teu_reduction","thermal_roi","confidence"):
        v = opt.get(key)
        if isinstance(v,(int,float)):
            nums[f"optimizer.{key}"] = float(v)

    scenario = opt.get("scenario") or {}
    for key in ("teu_reduction","teu_reduction_pct","va_teu_reduction","thermal_roi","confidence"):
        v = scenario.get(key)
        if isinstance(v,(int,float)):
            nums.setdefault(f"optimizer.{key}", float(v))

    quality = packet.get("state", {}).get("quality") or {}
    health = quality.get("health_score")
    if isinstance(health,(int,float)):
        nums["quality.health_score"] = float(health)

    return nums

def validate_answer(raw: dict, packet: dict) -> tuple[IntelligenceAnswer | None, dict]:
    issues = []
    try:
        answer = IntelligenceAnswer.model_validate(raw)
    except Exception as exc:
        return None, {"valid": False, "issues": [f"schema:{exc}"]}

    allowed_refs = {x["ref"] for x in packet.get("evidence_refs", [])}
    bad_refs = [r for r in answer.evidence_refs if r not in allowed_refs]
    if bad_refs:
        issues.append({"unsupported_evidence_refs": bad_refs})

    authoritative = collect_authoritative_numbers(packet)
    for key, value in answer.numeric_claims.items():
        if key not in authoritative:
            issues.append({"unsupported_numeric_key": key})
            continue
        if abs(float(value) - authoritative[key]) > max(1e-6, abs(authoritative[key]) * 1e-6):
            issues.append({"numeric_mismatch": {"key": key, "claimed": value, "authoritative": authoritative[key]}})

    quality = packet.get("state", {}).get("quality") or {}
    if quality.get("requires_human_review") and not answer.requires_human_review:
        issues.append({"review_gate_violation": True})
    if quality.get("requires_human_review") and answer.decision_status == "recommend":
        issues.append({"decision_status_violation": "recommend not allowed while quality gate requires review"})

    for action in answer.recommended_actions:
        unknown = set(action) - ALLOWED_ACTION_KEYS
        if unknown:
            issues.append({"unknown_action_fields": sorted(unknown)})

    return answer, {"valid": len(issues) == 0, "issues": issues, "authoritative_numbers": authoritative}
