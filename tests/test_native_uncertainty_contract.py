from app.intelligence.contracts import IntelligenceAnswer

def test_uncertainties_contract_is_list():
    a=IntelligenceAnswer(
        decision_status="review_required",
        headline="x",
        summary="x",
        recommended_actions=[],
        uncertainties=["one"],
        evidence_refs=[],
        numeric_claims={},
        requires_human_review=True,
    )
    assert a.uncertainties==["one"]
