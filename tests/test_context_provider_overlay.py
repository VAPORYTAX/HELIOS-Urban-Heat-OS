from app.contextforge.provider_overlay import STALE_PROVIDER_TRANSITION_KINDS
def test_transition_kinds_are_quarantined():
    assert STALE_PROVIDER_TRANSITION_KINDS == {"optimizer","exposure_metric","hotspot"}
