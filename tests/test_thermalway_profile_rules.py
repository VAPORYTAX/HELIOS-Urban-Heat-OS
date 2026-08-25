from types import SimpleNamespace
from app.thermalway.profile_rules import edge_allowed_for_profile,profile_edge_penalty
def test_no_steps_for_mobility_limited():
    assert not edge_allowed_for_profile(SimpleNamespace(highway="steps"),"mobility_limited")
def test_steps_penalized_for_older_adult():
    assert profile_edge_penalty(SimpleNamespace(highway="steps"),"older_adult")>1
