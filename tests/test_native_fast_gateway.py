from app.intelligence.router import choose_profile
from app.intelligence import gateway

def test_native_fast_helper_exists():
    assert callable(gateway.chat_native_fast)

def test_fast_profile_remains_compact():
    p=choose_profile("portfolio_optimization","investment",False)
    assert p["name"]=="fast"
    assert p["thinking"] is False
    assert p["include_raw_evidence"] is False

def test_deep_profile_preserved():
    p=choose_profile("scenario_comparison","planning",None)
    assert p["name"]=="deep"
    assert p["thinking"] is True
