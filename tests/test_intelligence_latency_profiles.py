from app.intelligence.router import choose_profile

def test_fast_portfolio_profile():
    p=choose_profile("portfolio_optimization","investment",False)
    assert p["name"]=="fast"
    assert p["thinking"] is False
    assert p["include_raw_evidence"] is False
    assert p["token_budget"]<=8000
    assert p["max_tokens"] == 2400

def test_deep_scenario_profile():
    p=choose_profile("scenario_comparison","planning",None)
    assert p["name"]=="deep"
    assert p["thinking"] is True
    assert p["include_raw_evidence"] is True
    assert p["token_budget"]>=12000

