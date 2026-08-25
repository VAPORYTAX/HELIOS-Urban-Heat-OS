from dataclasses import dataclass
from statistics import mean,pstdev
@dataclass(frozen=True)
class BaselineStats: mean_c:float; std_c:float; p90_c:float; sample_count:int
def percentile(values,q):
    xs=sorted(float(v) for v in values)
    if not xs: raise ValueError('values must not be empty')
    if len(xs)==1:return xs[0]
    pos=(len(xs)-1)*q; lo=int(pos); hi=min(lo+1,len(xs)-1); f=pos-lo
    return xs[lo]*(1-f)+xs[hi]*f
def compute_baseline(values):
    xs=[float(v) for v in values]
    if not xs: raise ValueError('cannot compute baseline from empty values')
    return BaselineStats(mean(xs),pstdev(xs) if len(xs)>1 else 0.0,percentile(xs,.9),len(xs))
def compute_anomaly(temp,base):
    if base is None:return None,None
    a=temp-base.mean_c; return a,(None if base.std_c<=1e-9 else a/base.std_c)
def compute_exceedance(temp,threshold): return max(0.0,temp-threshold)
def compute_persistence_hours(series,threshold):
    total=0.0
    for delta,temp in reversed(series):
        if temp<threshold:break
        total+=max(0.0,float(delta))
    return total
def clamp01(v):return max(0.0,min(1.0,v))
def severity_score(*,temp_c,anomaly_c,exceedance_c,persistence_hours,threshold_c):
    intensity=clamp01((temp_c-30)/18); anomaly=clamp01(((anomaly_c or 0)+1)/8); exceed=clamp01((exceedance_c or 0)/8); persistence=clamp01(persistence_hours/12)
    score=100*(.4*intensity+.25*anomaly+.2*exceed+.15*persistence)
    return round(score,3),{'intensity':round(intensity,4),'anomaly':round(anomaly,4),'exceedance':round(exceed,4),'persistence':round(persistence,4),'threshold_c':threshold_c}
def confidence_score(*,baseline_samples,source_type,has_environment):
    sample=clamp01(baseline_samples/30); src={'provider':.95,'observed':.95,'fixture':.8,'derived':.75,'modelled':.65,'assumed':.45}.get(source_type,.6); return round(clamp01(.55*src+.4*sample+(.05 if has_environment else 0)),3)
def severity_label(s):
    return 'critical' if s>=80 else 'high' if s>=60 else 'elevated' if s>=40 else 'watch' if s>=20 else 'routine'
