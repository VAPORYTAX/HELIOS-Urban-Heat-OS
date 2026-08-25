from app.provider_ops.service import compute_hazard
def test_hazard_bounded():
    *_,h=compute_hazard(50,5,30,30)
    assert 0<=h<=1
def test_negative_anomaly_does_not_raise_anomaly_component():
    _,a,_,_,_=compute_hazard(35,-2,0,0)
    assert a==0
