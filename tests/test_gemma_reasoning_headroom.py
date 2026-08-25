from app.intelligence.router import choose_profile

def test_fast_has_reasoning_headroom():
    p=choose_profile("portfolio_optimization","investment",False)
    assert p["name"]=="fast"
    assert p["thinking"] is False
    assert p["token_budget"]==7000
    assert p["include_raw_evidence"] is False
    assert p["max_tokens"]>=2400
    assert p["timeout_seconds"]>=180

def test_deep_bounded_but_larger():
    p=choose_profile("scenario_comparison","planning",None)
    assert p["name"]=="deep"
    assert p["max_tokens"]>choose_profile("portfolio_optimization","investment",False)["max_tokens"]
