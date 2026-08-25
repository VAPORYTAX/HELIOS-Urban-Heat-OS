from app.thermalway.alternatives import _call_yen_compat
def test_yen_compat_callable():
    assert callable(_call_yen_compat)
