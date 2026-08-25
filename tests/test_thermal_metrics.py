from app.thermal.metrics import *
def test_baseline():
 s=compute_baseline([30,32,34,36,38]); assert s.mean_c==34 and s.sample_count==5 and 36<=s.p90_c<=38
def test_anomaly():
 a,z=compute_anomaly(41,BaselineStats(35,2,38,20)); assert a==6 and z==3
def test_exceedance(): assert compute_exceedance(37,40)==0 and compute_exceedance(43,40)==3
def test_persistence(): assert compute_persistence_hours([(0,39),(1,41),(1,42),(1,43)],40)==3
def test_severity():
 score,p=severity_score(temp_c=50,anomaly_c=12,exceedance_c=10,persistence_hours=24,threshold_c=40); assert 0<=score<=100
def test_confidence(): assert confidence_score(baseline_samples=40,source_type='provider',has_environment=True)>confidence_score(baseline_samples=0,source_type='assumed',has_environment=False)
def test_labels(): assert [severity_label(x) for x in (10,30,50,70,90)]==['routine','watch','elevated','high','critical']
