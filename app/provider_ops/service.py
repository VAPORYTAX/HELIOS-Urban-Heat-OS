from sqlalchemy import desc,select
from app.db.models_provider_history import ProviderThermalBaseline,ProviderThermalStress
from app.db.models_demographics import CellDemographic
from app.db.models_provider_ops import ProviderOperationalMetric

MODEL_VERSION="provider-operational-hazard-v1"

def clamp(v): return max(0.0,min(1.0,float(v)))

def severity(h):
    if h>=0.80:return "critical"
    if h>=0.60:return "high"
    if h>=0.40:return "moderate"
    if h>=0.20:return "elevated"
    return "low"

def compute_hazard(current_c,z,persistence,exceedance):
    # Operational planning index, not a physiological or epidemiological risk model.
    temp=clamp((current_c-30.0)/15.0)
    anomaly=clamp(max(0.0,z or 0.0)/3.0)
    p=clamp((persistence or 0.0)/24.0)
    e=clamp((exceedance or 0.0)/24.0)
    h=0.45*temp+0.20*anomaly+0.20*p+0.15*e
    return temp,anomaly,p,e,clamp(h)

def rebuild_provider_metrics(db,area_id="phx-downtown"):
    baselines=db.execute(
        select(ProviderThermalBaseline).where(ProviderThermalBaseline.area_id==area_id)
        .order_by(desc(ProviderThermalBaseline.created_at))
    ).scalars().all()
    latest={}
    for b in baselines:
        latest.setdefault(b.cell_id,b)
    if len(latest)<4: raise RuntimeError("Provider baselines incomplete")

    stresses=db.execute(
        select(ProviderThermalStress).where(ProviderThermalStress.area_id==area_id)
        .order_by(desc(ProviderThermalStress.created_at))
    ).scalars().all()
    stress={}
    for s in stresses: stress.setdefault(s.cell_id,s)

    demos=db.execute(select(CellDemographic)).scalars().all()
    demo={d.cell_id:d for d in demos}

    old=db.execute(select(ProviderOperationalMetric).where(ProviderOperationalMetric.area_id==area_id)).scalars().all()
    for r in old: db.delete(r)

    out=[]
    for cid,b in sorted(latest.items()):
        d=demo.get(cid)
        if not d: raise RuntimeError(f"Missing demographics for {cid}")
        s=stress.get(cid)
        persistence=float(s.persistence_hours) if s else 0.0
        exceedance=float(s.exceedance_hours) if s else 0.0
        ts,az,ps,es,h=compute_hazard(float(b.current_c),b.z_score,persistence,exceedance)
        pop=float(d.population)
        vi=float(d.vulnerability_index)
        teu=h*pop
        # Preserve HELIOS VA-TEU semantics: amplified vulnerability-adjusted burden, not a subset count.
        va_teu=h*(pop*vi)*(1.0+vi)
        confidence=min(float(b.confidence),float(getattr(d,"confidence",0.85)),0.90 if s else 0.75)
        row=ProviderOperationalMetric(
            area_id=area_id,cell_id=cid,current_c=float(b.current_c),baseline_mean_c=float(b.mean_c),
            anomaly_c=float(b.anomaly_c),z_score=b.z_score,persistence_hours=persistence,
            exceedance_hours=exceedance,temperature_stress=ts,anomaly_stress=az,
            persistence_stress=ps,exceedance_stress=es,hazard_index=h,severity=severity(h),
            population=pop,vulnerability_index=vi,teu=teu,va_teu=va_teu,confidence=confidence,
            truth_category="provider_derived",model_version=MODEL_VERSION,
            evidence_json={
                "provider_baseline_id":b.id,
                "provider_stress_id":s.id if s else None,
                "demographic_id":d.id,
                "weights":{"temperature":0.45,"positive_anomaly":0.20,"persistence":0.20,"exceedance":0.15},
                "notes":[
                    "Operational planning index; not a medical outcome model.",
                    "Negative anomaly does not increase hazard.",
                    "VA-TEU is vulnerability-adjusted amplified burden and may exceed TEU."
                ]
            })
        db.add(row); out.append(row)
    db.commit()
    for r in out: db.refresh(r)
    return out
