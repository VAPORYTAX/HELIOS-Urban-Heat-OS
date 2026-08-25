from __future__ import annotations

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def simulate_cell(*, baseline_teu: float, baseline_vulnerable_teu: float,
                  interventions: list[dict], base_confidence: float):
    remaining_hazard_factor = 1.0
    remaining_exposure_factor = 1.0
    vulnerable_multiplier = 1.0
    confs = []

    for item in interventions:
        effect = item["effect_profile"]
        strength = clamp01(item["suitability_score"])
        hazard_cut = clamp01(effect["hazard_reduction"] * strength)
        exposure_cut = clamp01(effect["exposure_reduction"] * strength)

        # Multiplicative combination prevents impossible >100% reductions.
        remaining_hazard_factor *= (1.0 - hazard_cut)
        remaining_exposure_factor *= (1.0 - exposure_cut)
        vulnerable_multiplier *= max(0.75, 2.0 - effect["vulnerable_benefit_multiplier"])
        confs.append(item["confidence"])

    total_factor = clamp01(remaining_hazard_factor * remaining_exposure_factor)
    projected_teu = baseline_teu * total_factor
    projected_vulnerable = baseline_vulnerable_teu * total_factor * vulnerable_multiplier

    reduction = max(0.0, baseline_teu - projected_teu)
    vulnerable_reduction = max(0.0, baseline_vulnerable_teu - projected_vulnerable)

    confidence = min([base_confidence] + confs) if confs else base_confidence
    uncertainty = 1.0 - clamp01(confidence)

    lower = reduction * max(0.0, 1.0 - 0.60 * uncertainty)
    upper = reduction * (1.0 + 0.60 * uncertainty)

    return {
        "projected_teu": round(projected_teu, 6),
        "teu_reduction": round(reduction, 6),
        "projected_vulnerable_teu": round(projected_vulnerable, 6),
        "vulnerable_teu_reduction": round(vulnerable_reduction, 6),
        "confidence": round(confidence, 6),
        "lower_teu_reduction": round(lower, 6),
        "upper_teu_reduction": round(upper, 6),
        "remaining_factor": round(total_factor, 6),
    }
