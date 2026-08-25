from __future__ import annotations
import statistics
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy import desc, select
from geoalchemy2.shape import to_shape
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from app.db.models_fortyguard import FortyGuardIngestRun
from app.db.models_fortyguard_checkpoint import FortyGuardHistoryCheckpoint
from app.db.models_provider_history import ProviderThermalBaseline, ProviderThermalStress
from app.db.models_thermal import ThermalCell, ThermalObservation
from app.fortyguard_live.client import submit_heatmap, wait_result

PHX=ZoneInfo("America/Phoenix")
TERMINAL={"COMPLETE_WITH_DATA","COMPLETE_NO_DATA"}

def _aoi(cells, area_id):
    union=unary_union([to_shape(c.geometry) for c in cells])
    return {"type":"FeatureCollection","features":[{"type":"Feature","properties":{"area_id":area_id},"geometry":mapping(union)}]}

def _map_property(features,cells,prop):
    vals={c.id:[] for c in cells}
    for f in features:
        p=f.get("properties") or {}
        if prop not in p or not isinstance(p[prop],(int,float)): continue
        g=shape(f["geometry"]); v=float(p[prop])
        for c in cells:
            inter=g.intersection(to_shape(c.geometry))
            if inter.is_empty or inter.area<=0: continue
            vals[c.id].append((v,inter.area))
    out={}
    for cid,rows in vals.items():
        total=sum(w for _,w in rows)
        if total>0: out[cid]=sum(v*w for v,w in rows)/total
    return out

def _infer_numeric_property(features, preferred):
    keys=[]
    for f in features:
        p=f.get("properties") or {}
        for k,v in p.items():
            if isinstance(v,(int,float)) and k!="tile_id" and k not in keys:
                keys.append(k)
    for p in preferred:
        if p in keys: return p
    if len(keys)==1: return keys[0]
    return None

def _checkpoint(db,key,area,kind,req_date,payload):
    row=db.execute(select(FortyGuardHistoryCheckpoint).where(FortyGuardHistoryCheckpoint.request_key==key)).scalar_one_or_none()
    if row: return row
    row=FortyGuardHistoryCheckpoint(
        request_key=key,area_id=area,request_kind=kind,request_date=req_date,
        state="PENDING",payload_json=payload,result_json={}
    )
    db.add(row); db.commit(); db.refresh(row); return row

def _run_request(db,row):
    if row.state in TERMINAL:
        print(f"SKIP {row.request_key}: {row.state}",flush=True)
        return row

    if not row.activity_id:
        aid=submit_heatmap(row.payload_json)
        row.activity_id=aid
        row.state="SUBMITTED"
        row.updated_at=datetime.now(timezone.utc)
        db.commit()
        print(f"SUBMITTED {row.request_key}: {aid}",flush=True)
    else:
        print(f"RESUME {row.request_key}: {row.activity_id}",flush=True)

    result=wait_result(row.activity_id)
    features=((result.get("map_data") or {}).get("features") or [])
    stats=result.get("stats_data") or {}
    row.state="COMPLETE_WITH_DATA" if features else "COMPLETE_NO_DATA"
    row.result_json={
        "feature_count":len(features),
        "stats_keys":sorted(stats.keys()) if isinstance(stats,dict) else [],
        "result":result if features else {"map_data":{"type":"FeatureCollection","features":[]},"stats_data":stats},
    }
    row.updated_at=datetime.now(timezone.utc)
    db.commit(); db.refresh(row)
    print(f"{row.request_key}: {row.state} features={len(features)}",flush=True)
    return row

def build_checkpointed_history(db, area_id="phx-downtown", days=7, threshold_c=30.0, min_data_days=4):
    cells=db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all()
    if len(cells)<1: raise RuntimeError("No thermal cells found")

    latest=db.execute(
        select(FortyGuardIngestRun).where(FortyGuardIngestRun.area_id==area_id,FortyGuardIngestRun.status=="complete")
        .order_by(desc(FortyGuardIngestRun.target_time)).limit(1)
    ).scalar_one_or_none()
    if not latest: raise RuntimeError("No live FortyGuard ingest exists")

    local_anchor=latest.target_time.astimezone(PHX)
    aoi=_aoi(cells,area_id)

    # Record the already-spent exact-hour D-1 request as provider no-data so it is never retried.
    legacy_key=f"{area_id}:single-hour:{(local_anchor-timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')}"
    legacy=db.execute(select(FortyGuardHistoryCheckpoint).where(FortyGuardHistoryCheckpoint.request_key==legacy_key)).scalar_one_or_none()
    if not legacy:
        legacy=FortyGuardHistoryCheckpoint(
            request_key=legacy_key,area_id=area_id,request_kind="single_hour_legacy",
            request_date=(local_anchor-timedelta(days=1)).date(),
            activity_id="73ff7877-056f-4410-87e3-0d508c2a947b",
            state="COMPLETE_NO_DATA",
            payload_json={"note":"Legacy exact-hour request completed with zero features; do not retry."},
            result_json={"feature_count":0},
        )
        db.add(legacy); db.commit()

    day_rows=[]
    for offset in range(1,days+1):
        d=(local_anchor.date()-timedelta(days=offset))
        key=f"{area_id}:single-day:{d.isoformat()}"
        payload={
            "polygon_aoi":aoi,
            "date_time":{"start_date":d.isoformat(),"filter_type":3},
            "granularity":100,
            "analytic_type":"tcm",
        }
        row=_checkpoint(db,key,area_id,"single_day",d,payload)
        day_rows.append(_run_request(db,row))

    usable=[r for r in day_rows if r.state=="COMPLETE_WITH_DATA"]
    if len(usable)<min_data_days:
        raise RuntimeError(
            f"Only {len(usable)} of {days} daily provider requests returned data; "
            f"minimum {min_data_days} required. Completed no-data jobs were checkpointed and will not be retried."
        )

    # Build cell-level daily series.
    series={c.id:[] for c in cells}
    activity_ids=[]
    for r in usable:
        result=(r.result_json or {}).get("result") or {}
        feats=((result.get("map_data") or {}).get("features") or [])
        prop=_infer_numeric_property(feats,["average_temperature","mean_temperature","temperature"])
        if not prop:
            raise RuntimeError(f"Could not identify temperature property for {r.request_key}")
        mapped=_map_property(feats,cells,prop)
        if not mapped:
            raise RuntimeError(f"No daily features mapped for {r.request_key}")
        activity_ids.append(r.activity_id)
        for cid,v in mapped.items():
            series[cid].append(v)

    current={}
    for c in cells:
        obs=db.execute(
            select(ThermalObservation).where(
                ThermalObservation.cell_id==c.id,
                ThermalObservation.source_name=="fortyguard"
            ).order_by(desc(ThermalObservation.observed_at)).limit(1)
        ).scalar_one_or_none()
        if not obs: raise RuntimeError(f"No current FortyGuard observation for {c.id}")
        current[c.id]=float(obs.temperature_c)

    # Remove prior baseline rows from this operational provider layer to avoid duplicate latest ambiguity.
    for old in db.execute(select(ProviderThermalBaseline).where(ProviderThermalBaseline.area_id==area_id)).scalars().all():
        db.delete(old)

    baseline_out=[]
    for cid,values in series.items():
        if len(values)<min_data_days:
            continue
        mean=statistics.fmean(values)
        med=statistics.median(values)
        std=statistics.pstdev(values)
        anomaly=current[cid]-mean
        z=None if std<1e-9 else anomaly/std
        confidence=min(0.95,0.60+0.05*len(values))
        row=ProviderThermalBaseline(
            area_id=area_id,cell_id=cid,local_hour=local_anchor.hour,sample_days=len(values),
            mean_c=mean,median_c=med,std_c=std,min_c=min(values),max_c=max(values),
            current_c=current[cid],anomaly_c=anomaly,z_score=z,confidence=confidence,
            truth_category="provider",source_activity_ids=activity_ids,
        )
        db.add(row)
        baseline_out.append({
            "cell_id":cid,"sample_days":len(values),"mean_c":mean,"median_c":med,"std_c":std,
            "current_c":current[cid],"anomaly_c":anomaly,"z_score":z,"confidence":confidence
        })

    # Native provider stress for previous completed day.
    stress_day=local_anchor.date()-timedelta(days=1)
    analytics={}
    for kind in ("persistence","exceedance"):
        key=f"{area_id}:{kind}:{stress_day.isoformat()}:{threshold_c}"
        payload={
            "polygon_aoi":aoi,
            "date_time":{"start_date":stress_day.isoformat(),"start_time":"00:00","end_time":"23:00","filter_type":2},
            "granularity":100,"analytic_type":kind,
            "threshold":threshold_c,"direction":"above",
        }
        analytics[kind]=_run_request(db,_checkpoint(db,key,area_id,kind,stress_day,payload))

    stress_maps={}
    for kind,row in analytics.items():
        if row.state!="COMPLETE_WITH_DATA":
            stress_maps[kind]={}
            continue
        result=(row.result_json or {}).get("result") or {}
        feats=((result.get("map_data") or {}).get("features") or [])
        pref=[kind,f"{kind}_hours","hours","value","analytic_value"]
        prop=_infer_numeric_property(feats,pref)
        if not prop:
            print(f"WARNING: could not infer {kind} tile property; stress metric remains unavailable",flush=True)
            stress_maps[kind]={}
        else:
            stress_maps[kind]=_map_property(feats,cells,prop)

    # Replace prior stress rows only if both native analytics mapped.
    if len(stress_maps["persistence"])==len(cells) and len(stress_maps["exceedance"])==len(cells):
        for old in db.execute(select(ProviderThermalStress).where(ProviderThermalStress.area_id==area_id)).scalars().all():
            db.delete(old)
        for c in cells:
            db.add(ProviderThermalStress(
                area_id=area_id,cell_id=c.id,period_date=stress_day,threshold_c=threshold_c,
                persistence_hours=float(stress_maps["persistence"][c.id]),
                exceedance_hours=float(stress_maps["exceedance"][c.id]),
                truth_category="provider",confidence=0.90,
                activity_ids={
                    "persistence":analytics["persistence"].activity_id,
                    "exceedance":analytics["exceedance"].activity_id,
                },
            ))
    db.commit()

    return {
        "area_id":area_id,
        "requested_days":days,
        "usable_provider_days":len(usable),
        "no_data_days":[str(r.request_date) for r in day_rows if r.state=="COMPLETE_NO_DATA"],
        "baseline":baseline_out,
        "stress_day":str(stress_day),
        "persistence_available":len(stress_maps["persistence"])==len(cells),
        "exceedance_available":len(stress_maps["exceedance"])==len(cells),
        "checkpoint_states":{r.request_key:r.state for r in day_rows+[analytics["persistence"],analytics["exceedance"]]},
        "legacy_no_data_activity":"73ff7877-056f-4410-87e3-0d508c2a947b",
    }
