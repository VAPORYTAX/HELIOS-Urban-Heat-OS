from types import SimpleNamespace
from app.thermalway.router import _cost
def test_fastest_still_accumulates_tec():
    e=SimpleNamespace(length_m=100.0,covered=None)
    m=SimpleNamespace(current_c=35.0,vulnerability_index=.5,confidence=.9)
    cost,tec=_cost(e,m,"older_adult","fastest")
    assert cost>0 and tec>0
def test_safe_cost_penalizes_tec():
    e=SimpleNamespace(length_m=100.0,covered=None)
    m=SimpleNamespace(current_c=35.0,vulnerability_index=.5,confidence=.9)
    fast,_=_cost(e,m,"standard","fastest")
    safe,_=_cost(e,m,"standard","thermal_safe")
    assert safe>fast
