from app.counterfactual.engine import simulate_cell

def intervention(h=0.1, e=0.05, s=0.9, c=0.8, v=1.05):
    return {
        "effect_profile": {
            "hazard_reduction": h,
            "exposure_reduction": e,
            "vulnerable_benefit_multiplier": v,
        },
        "suitability_score": s,
        "confidence": c,
    }

def test_intervention_reduces_teu():
    r = simulate_cell(
        baseline_teu=500,
        baseline_vulnerable_teu=200,
        interventions=[intervention()],
        base_confidence=0.85,
    )
    assert r["projected_teu"] < 500
    assert r["teu_reduction"] > 0

def test_multiple_interventions_do_not_produce_negative_teu():
    items = [intervention(h=0.8, e=0.8) for _ in range(5)]
    r = simulate_cell(
        baseline_teu=500,
        baseline_vulnerable_teu=200,
        interventions=items,
        base_confidence=0.8,
    )
    assert r["projected_teu"] >= 0

def test_uncertainty_contains_point_estimate():
    r = simulate_cell(
        baseline_teu=500,
        baseline_vulnerable_teu=200,
        interventions=[intervention(c=0.6)],
        base_confidence=0.7,
    )
    assert r["lower_teu_reduction"] <= r["teu_reduction"] <= r["upper_teu_reduction"]
