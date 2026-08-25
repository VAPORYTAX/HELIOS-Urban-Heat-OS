from math import exp
from sqlalchemy import delete,select
from geoalchemy2.shape import to_shape
from app.db.models_exposure import Facility
from app.db.models_thermal import ThermalCell
from app.db.models_thermalway_access import ThermalWayAccessibilityScore,ThermalWayCriticalJourney
from app.thermalway.router import compare,route
CRITICAL={"health":{"hospital","clinic","healthcare","doctors"},"school":{"school","college","university"},"safe_haven":{"library","community_centre","shelter","public_building","fire_station","police"}}
def xy(f):
    for a in ("geometry","geom","location"):
        if hasattr(f,a) and getattr(f,a) is not None:
            g=to_shape(getattr(f,a)); return g.x,g.y
def label(f): return " ".join(str(getattr(f,a,"") or "") for a in ("facility_type","category","kind","amenity","name")).lower()
def fdict(f): return {"id":str(getattr(f,"id","")),"name":getattr(f,"name",None),"type":getattr(f,"facility_type",None) or getattr(f,"category",None) or getattr(f,"kind",None)}
def nearest(fs,lon,lat,hints,n=8):
    r=[]
    for f in fs:
        if not any(h in label(f) for h in hints): continue
        p=xy(f)
        if p:r.append(((p[0]-lon)**2+(p[1]-lat)**2,f,p))
    r.sort(key=lambda x:x[0]); return r[:n]
def build_accessibility(db,area_id="phx-downtown",profile="older_adult"):
    cells=db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all()
    fs=db.execute(select(Facility)).scalars().all()
    db.execute(delete(ThermalWayAccessibilityScore).where(ThermalWayAccessibilityScore.area_id==area_id))
    hints=set().union(*CRITICAL.values()); out=[]
    for c in cells:
        g=to_shape(c.centroid if getattr(c,"centroid",None) is not None else c.geometry).centroid
        rr=[]
        for _,f,p in nearest(fs,g.x,g.y,hints):
            try:
                r=route(db,g.x,g.y,p[0],p[1],"thermal_safe",profile,area_id,"dijkstra"); rr.append((r.thermal_exposure_cost,r.duration_min,f,r))
            except Exception: pass
        if not rr: raise RuntimeError(f"No routable critical facility from {c.id}")
        rr.sort(key=lambda x:(x[0],x[1])); tec,dur,f,r=rr[0]
        score=max(0,min(100,100*exp(-dur/20)*exp(-tec/1500)))
        row=ThermalWayAccessibilityScore(area_id=area_id,cell_id=c.id,traveler_profile=profile,facility_count=len(rr),best_duration_min=dur,best_tec=tec,accessibility_score=score,best_facility_json={**fdict(f),"route_id":r.id},truth_category="real_osm_observed_facility_provider_thermal_modelled_access")
        db.add(row);out.append(row)
    db.commit(); return out
def build_critical_journeys(db,area_id="phx-downtown"):
    cells=db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all()
    fs=db.execute(select(Facility)).scalars().all()
    db.execute(delete(ThermalWayCriticalJourney).where(ThermalWayCriticalJourney.area_id==area_id))
    profiles={"health":"older_adult","school":"child","safe_haven":"mobility_limited"}; out=[]
    for c in cells:
        g=to_shape(c.centroid if getattr(c,"centroid",None) is not None else c.geometry).centroid
        for jt,hints in CRITICAL.items():
            chosen=None
            for _,f,p in nearest(fs,g.x,g.y,hints,6):
                try:
                    fast,safe=compare(db,g.x,g.y,p[0],p[1],profiles[jt],area_id); chosen=(f,fast,safe); break
                except Exception: pass
            if not chosen: continue
            f,fast,safe=chosen; saved=max(0,fast.thermal_exposure_cost-safe.thermal_exposure_cost); extra=max(0,safe.duration_min-fast.duration_min)
            protection=max(0,min(100,100*(saved/max(fast.thermal_exposure_cost,1e-9))*exp(-extra/20)))
            row=ThermalWayCriticalJourney(area_id=area_id,journey_type=jt,origin_cell_id=c.id,traveler_profile=profiles[jt],facility_json=fdict(f),fastest_json={"route_id":fast.id,"duration_min":fast.duration_min,"tec":fast.thermal_exposure_cost},thermal_safe_json={"route_id":safe.id,"duration_min":safe.duration_min,"tec":safe.thermal_exposure_cost},thermal_cost_saved=saved,extra_minutes=extra,protection_score=protection,truth_category="real_osm_observed_facility_provider_thermal_modelled_protection")
            db.add(row);out.append(row)
    db.commit(); return out
