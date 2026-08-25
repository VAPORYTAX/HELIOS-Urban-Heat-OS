from __future__ import annotations
import statistics, time
from datetime import timedelta
from sqlalchemy import desc, select
from geoalchemy2.shape import to_shape
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from app.db.models_fortyguard import FortyGuardIngestRun
from app.db.models_provider_history import ProviderThermalBaseline, ProviderThermalStress
from app.db.models_thermal import ThermalCell, ThermalObservation
from app.fortyguard_live.client import submit_heatmap, wait_result

def _aoi(cells, area_id):
    union=unary_union([to_shape(c.geometry) for c in cells])
    return {"type":"FeatureCollection","features":[{"type":"Feature","properties":{"area_id":area_id},"geometry":mapping(union)}]}

def _map_property(features,cells,prop):
    vals={c.id:[] for c in cells}
    for f in features:
        g=shape(f["geometry"]); p=f.get("properties") or {}
        if prop not in p: continue
        v=float(p[prop])
        for c in cells:
            inter=g.intersection(to_shape(c.geometry))
            if inter.is_empty or inter.area<=0: continue
            vals[c.id].append((v,inter.area))
    out={}
    for cid,rows in vals.items():
        total=sum(w for _,w in rows)
        if total>0: out[cid]=sum(v*w for v,w in rows)/total
    return out

def _submit_and_wait(payload, label):
    aid=submit_heatmap(payload)
    print(f"{label} SUBMITTED: {aid}",flush=True)
    result=wait_result(aid)
    print(f"{label} COMPLETED",flush=True)
    time.sleep(1)
    return aid,result

def build_operational_history(db, area_id="phx-downtown", days=7, threshold_c=30.0):
    if days < 5 or days > 14:
        raise ValueError("days must be 5..14 for the operational baseline")
    cells=db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all()
    if not cells: raise RuntimeError("No thermal cells")

    latest_run=db.execute(
        select(FortyGuardIngestRun).where(FortyGuardIngestRun.area_id==area_id,FortyGuardIngestRun.status=="complete")
        .order_by(desc(FortyGuardIngestRun.target_time)).limit(1)
    ).scalar_one_or_none()
    if not latest_run: raise RuntimeError("No live FortyGuard provider ingest found")

    current_obs={}
    for c in cells:
        obs=db.execute(
            select(ThermalObservation).where(
                ThermalObservation.cell_id==c.id,
                ThermalObservation.source_name=="fortyguard"
            ).order_by(desc(ThermalObservation.observed_at)).limit(1)
        ).scalar_one_or_none()
        if not obs: raise RuntimeError(f"No provider observation for {c.id}")
        current_obs[c.id]=float(obs.temperature_c)

    local_target=latest_run.target_time.astimezone(__import__("zoneinfo").ZoneInfo("America/Phoenix"))
    aoi=_aoi(cells,area_id)

    series={c.id:[] for c in cells}
    activity_ids=[]
    for offset in range(1,days+1):
        when=local_target-timedelta(days=offset)
        payload={
            "polygon_aoi":aoi,
            "date_time":{"start_date":when.strftime("%Y-%m-%d"),"start_time":when.strftime("%H:%M"),"filter_type":1},
            "granularity":100,
            "analytic_type":"tcm",
        }
        aid,result=_submit_and_wait(payload,f"BASELINE D-{offset}")
        activity_ids.append(aid)
        features=((result.get("map_data") or {}).get("features") or [])
        mapped=_map_property(features,cells,"average_temperature")
        if len(mapped)!=len(cells): raise RuntimeError(f"Historical mapping incomplete for {when.date()}")
        for cid,v in mapped.items(): series[cid].append(v)

    # Previous fully completed Phoenix day, using provider-native continuous analytics.
    stress_day=(local_target.date()-timedelta(days=1))
    common={
        "polygon_aoi":aoi,
        "date_time":{"start_date":stress_day.strftime("%Y-%m-%d"),"start_time":"00:00","end_time":"23:00","filter_type":2},
        "granularity":100,
        "threshold":threshold_c,
        "direction":"above",
    }
    pp=dict(common); pp["analytic_type"]="persistence"
    pa,pres=_submit_and_wait(pp,"PERSISTENCE")
    ep=dict(common); ep["analytic_type"]="exceedance"
    ea,ex=_submit_and_wait(ep,"EXCEEDANCE")

    pmap=_map_property(((pres.get("map_data") or {}).get("features") or []),cells,"value")
    emap=_map_property(((ex.get("map_data") or {}).get("features") or []),cells,"value")
    # Some accounts may return the analytic under a named property. Discover safely.
    if len(pmap)!=len(cells):
        feats=((pres.get("map_data") or {}).get("features") or [])
        keys=set()
        for f in feats: keys.update((f.get("properties") or {}).keys())
        for candidate in ("persistence","persistence_hours","hours","analytic_value"):
            if candidate in keys:
                pmap=_map_property(feats,cells,candidate); break
    if len(emap)!=len(cells):
        feats=((ex.get("map_data") or {}).get("features") or [])
        keys=set()
        for f in feats: keys.update((f.get("properties") or {}).keys())
        for candidate in ("exceedance","exceedance_hours","hours","analytic_value"):
            if candidate in keys:
                emap=_map_property(feats,cells,candidate); break
    if len(pmap)!=len(cells) or len(emap)!=len(cells):
        raise RuntimeError("Provider analytic property name not recognized; inspect returned tile properties before storing stress metrics")

    baseline_rows=[]
    for cid,values in series.items():
        mean=statistics.fmean(values)
        median=statistics.median(values)
        std=statistics.pstdev(values)
        current=current_obs[cid]
        anomaly=current-mean
        z=None if std<1e-9 else anomaly/std
        conf=min(0.95,0.70+0.025*len(values))
        row=ProviderThermalBaseline(
            area_id=area_id,cell_id=cid,local_hour=local_target.hour,sample_days=len(values),
            mean_c=mean,median_c=median,std_c=std,min_c=min(values),max_c=max(values),
            current_c=current,anomaly_c=anomaly,z_score=z,confidence=conf,
            truth_category="provider",source_activity_ids=activity_ids)
        db.add(row); baseline_rows.append(row)

        srow=ProviderThermalStress(
            area_id=area_id,cell_id=cid,period_date=stress_day,threshold_c=threshold_c,
            persistence_hours=float(pmap[cid]),exceedance_hours=float(emap[cid]),
            truth_category="provider",confidence=0.90,
            activity_ids={"persistence":pa,"exceedance":ea})
        db.add(srow)

    db.commit()
    return {
        "area_id":area_id,"local_hour":local_target.hour,"sample_days":days,
        "threshold_c":threshold_c,"baseline_activity_ids":activity_ids,
        "persistence_activity_id":pa,"exceedance_activity_id":ea,
        "baselines":[{
            "cell_id":r.cell_id,"mean_c":r.mean_c,"median_c":r.median_c,"std_c":r.std_c,
            "current_c":r.current_c,"anomaly_c":r.anomaly_c,"z_score":r.z_score,"confidence":r.confidence
        } for r in baseline_rows],
        "stress":[{"cell_id":cid,"persistence_hours":pmap[cid],"exceedance_hours":emap[cid]} for cid in sorted(pmap)]
    }
