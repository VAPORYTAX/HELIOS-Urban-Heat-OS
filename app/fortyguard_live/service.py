from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from uuid import uuid4
from geoalchemy2.shape import to_shape
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
from sqlalchemy import select
from app.db.models_fortyguard import FortyGuardIngestRun
from app.db.models_thermal import ThermalCell,ThermalObservation
from app.fortyguard_live.client import submit_heatmap,wait_result

PHX=ZoneInfo("America/Phoenix")

def target_hour():
    return (datetime.now(PHX)-timedelta(hours=1)).replace(minute=0,second=0,microsecond=0)

def map_tiles(features,cells):
    vals={c.id:[] for c in cells}
    for f in features:
        g=shape(f["geometry"]); p=f.get("properties") or {}
        t=float(p["average_temperature"]); tid=p.get("tile_id")
        for c in cells:
            inter=g.intersection(to_shape(c.geometry))
            if inter.is_empty or inter.area<=0: continue
            vals[c.id].append((t,inter.area,tid))
    out=[]
    for cid,rows in vals.items():
        total=sum(w for _,w,_ in rows)
        if total>0:
            out.append({"cell_id":cid,"temperature_c":sum(t*w for t,w,_ in rows)/total,
                        "tile_ids":[tid for _,_,tid in rows],"tile_count":len(rows)})
    return out

def observation_kwargs(cell_id,when,temp,aid,stats):
    cols={c.name for c in ThermalObservation.__table__.columns}
    candidates={
        "id":str(uuid4()),"cell_id":cell_id,"observed_at":when.astimezone(timezone.utc),
        "temperature_c":temp,"source_type":"provider","source_name":"fortyguard","source_ref":f"fortyguard:{aid}",
        "provider":"fortyguard","truth_category":"provider","confidence":0.95,
        "metadata_json":{"activity_id":aid,"stats":stats},"raw_json":{"activity_id":aid,"stats":stats},
    }
    data={k:v for k,v in candidates.items() if k in cols}
    required={c.name for c in ThermalObservation.__table__.columns
              if not c.nullable and c.default is None and c.server_default is None and not c.primary_key}
    missing=required-set(data)
    if missing: raise RuntimeError(f"Unsupported required ThermalObservation columns: {sorted(missing)}")
    return data

def ingest_live_hour(db,area_id="phx-downtown"):
    cells=db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all()
    if not cells: raise RuntimeError("No thermal cells")
    when=target_hour()
    union=unary_union([to_shape(c.geometry) for c in cells])
    payload={
      "polygon_aoi":{"type":"FeatureCollection","features":[{"type":"Feature","properties":{"area_id":area_id},"geometry":mapping(union)}]},
      "date_time":{"start_date":when.strftime("%Y-%m-%d"),"start_time":when.strftime("%H:%M"),"filter_type":1},
      "granularity":100,"analytic_type":"tcm"
    }
    aid=submit_heatmap(payload)
    print(f"SUBMITTED: {aid}",flush=True)
    result=wait_result(aid)
    features=((result.get("map_data") or {}).get("features") or [])
    stats=result.get("stats_data") or {}
    mapped=map_tiles(features,cells)
    if not mapped: raise RuntimeError("No FortyGuard tiles mapped to HELIOS cells")
    for row in mapped:
        db.add(ThermalObservation(**observation_kwargs(row["cell_id"],when,row["temperature_c"],aid,stats)))
    run=FortyGuardIngestRun(area_id=area_id,activity_id=aid,status="complete",
        target_time=when.astimezone(timezone.utc),granularity_m=100,analytic_type="tcm",
        tile_count=len(features),cells_updated=len(mapped),stats_json=stats,mapping_json={"cells":mapped},
        completed_at=datetime.now(timezone.utc))
    db.add(run); db.commit(); db.refresh(run); return run
