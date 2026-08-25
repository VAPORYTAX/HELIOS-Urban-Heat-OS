import statistics
def test_operational_baseline_math():
    x=[30,31,32,33,34,35,36]
    assert statistics.fmean(x)==33
    assert statistics.median(x)==33
    assert round(statistics.pstdev(x),6)==2.0
