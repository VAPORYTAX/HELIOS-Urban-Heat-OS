from types import SimpleNamespace

from app.thermalway.router import _cost


def edge(covered="no"):
    return SimpleNamespace(length_m=100.0, covered=covered)


def metric(temp):
    return SimpleNamespace(current_c=temp, vulnerability_index=0.4, confidence=0.8)


def test_hot_field_cool_and_safe_penalize_heat():
    fastest, fastest_tec = _cost(edge(), metric(42.0), "standard", "fastest")
    cool, cool_tec = _cost(edge(), metric(42.0), "standard", "cool")
    safe, safe_tec = _cost(edge(), metric(42.0), "standard", "thermal_safe")
    assert cool > fastest
    assert safe > fastest
    assert cool_tec > 0
    assert safe_tec > 0
    assert fastest_tec > 0


def test_hot_field_warm_mode_has_no_fabricated_cold_stress():
    fastest, _ = _cost(edge(), metric(42.0), "standard", "fastest")
    warm, warm_tec = _cost(edge(), metric(42.0), "standard", "warm")
    assert warm == fastest
    assert warm_tec == 0


def test_cold_field_warm_and_safe_penalize_cold():
    fastest, _ = _cost(edge(), metric(8.0), "older_adult", "fastest")
    warm, warm_tec = _cost(edge(), metric(8.0), "older_adult", "warm")
    safe, safe_tec = _cost(edge(), metric(8.0), "older_adult", "thermal_safe")
    assert warm > fastest
    assert safe > fastest
    assert warm_tec > 0
    assert safe_tec > 0
