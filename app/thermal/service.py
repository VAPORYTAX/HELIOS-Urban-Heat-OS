from datetime import datetime,timedelta,timezone
from geoalchemy2.shape import from_shape,to_shape
from shapely.geometry import shape,MultiPolygon
from sqlalchemy import desc,select
from app.db.models_thermal import ThermalBaseline,ThermalCell,ThermalHotspot,ThermalMetric,ThermalObservation
from app.thermal.metrics import BaselineStats,compute_anomaly,compute_baseline,compute_exceedance,compute_persistence_hours,confidence_score,severity_label,severity_score
def upsert_cell(db,item):
    row=db.get(ThermalCell,item.id); geom=shape(item.geometry)
    if row is None:
        row=ThermalCell(id=item.id,area_id=item.area_id,grid_key=item.grid_key,resolution_m=item.resolution_m,geometry=from_shape(geom,srid=4326),centroid=from_shape(geom.centroid,srid=4326)); db.add(row)
    else: row.geometry=from_shape(geom,srid=4326); row.centroid=from_shape(geom.centroid,srid=4326); row.resolution_m=item.resolution_m
    db.commit(); db.refresh(row); return row
def ingest_observation(db,item):
    row=db.execute(select(ThermalObservation).where(ThermalObservation.cell_id==item.cell_id,ThermalObservation.observed_at==item.observed_at,ThermalObservation.source_name==item.source_name)).scalar_one_or_none()
    if row:return row
    row=ThermalObservation(cell_id=item.cell_id,observed_at=item.observed_at,temperature_c=item.temperature_c,apparent_temperature_c=item.apparent_temperature_c,humidity_pct=item.humidity_pct,heat_index_c=item.heat_index_c,source_type=item.source_type,source_name=item.source_name,source_activity_id=item.source_activity_id,quality_label=item.quality_label,metadata_json=item.metadata); db.add(row); db.commit(); db.refresh(row); return row
def bucket_key(dt): return f'm{dt.month:02d}-h{dt.hour:02d}'
def rebuild_baseline_for_cell(db,cell_id,minimum_samples=3):
    obs=db.execute(select(ThermalObservation).where(ThermalObservation.cell_id==cell_id).order_by(ThermalObservation.observed_at)).scalars().all(); groups={}
    for o in obs: groups.setdefault(bucket_key(o.observed_at),[]).append(o.temperature_c)
    rows=[]
    for k,v in groups.items():
      if len(v)<minimum_samples:continue
      s=compute_baseline(v); row=db.execute(select(ThermalBaseline).where(ThermalBaseline.cell_id==cell_id,ThermalBaseline.bucket_key==k)).scalar_one_or_none()
      if row is None: row=ThermalBaseline(cell_id=cell_id,bucket_key=k); db.add(row)
      row.mean_c=s.mean_c; row.std_c=s.std_c; row.p90_c=s.p90_c; row.sample_count=s.sample_count; row.computed_at=datetime.now(timezone.utc); rows.append(row)
    db.commit(); return rows
def _baseline_for(db,cell_id,dt):
    r=db.execute(select(ThermalBaseline).where(ThermalBaseline.cell_id==cell_id,ThermalBaseline.bucket_key==bucket_key(dt))).scalar_one_or_none(); return None if not r else BaselineStats(r.mean_c,r.std_c,r.p90_c,r.sample_count)
def compute_metric_for_observation(db,obs,threshold_c=40):
    base=_baseline_for(db,obs.cell_id,obs.observed_at); anomaly,z=compute_anomaly(obs.temperature_c,base); exc=compute_exceedance(obs.temperature_c,threshold_c)
    hist=db.execute(select(ThermalObservation).where(ThermalObservation.cell_id==obs.cell_id,ThermalObservation.observed_at<=obs.observed_at,ThermalObservation.observed_at>=obs.observed_at-timedelta(hours=24)).order_by(ThermalObservation.observed_at)).scalars().all(); intervals=[]; prev=None
    for h in hist: intervals.append((0 if prev is None else max(0,(h.observed_at-prev.observed_at).total_seconds()/3600),h.temperature_c)); prev=h
    persistence=compute_persistence_hours(intervals,threshold_c); score,parts=severity_score(temp_c=obs.temperature_c,anomaly_c=anomaly,exceedance_c=exc,persistence_hours=persistence,threshold_c=threshold_c); conf=confidence_score(baseline_samples=base.sample_count if base else 0,source_type=obs.source_type,has_environment=obs.humidity_pct is not None or obs.apparent_temperature_c is not None)
    row=db.execute(select(ThermalMetric).where(ThermalMetric.cell_id==obs.cell_id,ThermalMetric.observed_at==obs.observed_at)).scalar_one_or_none()
    if row is None: row=ThermalMetric(cell_id=obs.cell_id,observed_at=obs.observed_at); db.add(row)
    row.anomaly_c=anomaly; row.z_score=z; row.exceedance_c=exc; row.persistence_hours=persistence; row.severity_score=score; row.confidence=conf; row.components_json=parts; db.commit(); db.refresh(row); return row
def latest_metrics_for_area(db,area_id):
    ids=db.execute(select(ThermalCell.id).where(ThermalCell.area_id==area_id)).scalars().all(); out=[]
    for cid in ids:
      r=db.execute(select(ThermalMetric).where(ThermalMetric.cell_id==cid).order_by(desc(ThermalMetric.observed_at)).limit(1)).scalar_one_or_none()
      if r:out.append(r)
    return out
def detect_hotspot(db,area_id,min_score=40):
    metrics=[m for m in latest_metrics_for_area(db,area_id) if m.severity_score>=min_score]
    if not metrics:return None
    ids=[m.cell_id for m in metrics]; cells=db.execute(select(ThermalCell).where(ThermalCell.id.in_(ids))).scalars().all(); obs=[]
    for cid in ids:
      r=db.execute(select(ThermalObservation).where(ThermalObservation.cell_id==cid).order_by(desc(ThermalObservation.observed_at)).limit(1)).scalar_one_or_none()
      if r:obs.append(r)
    merged=to_shape(cells[0].geometry)
    for c in cells[1:]:merged=merged.union(to_shape(c.geometry))
    if merged.geom_type=='Polygon':merged=MultiPolygon([merged])
    anomalies=[m.anomaly_c for m in metrics if m.anomaly_c is not None]; mean_score=sum(m.severity_score for m in metrics)/len(metrics)
    row=ThermalHotspot(area_id=area_id,detected_at=max(m.observed_at for m in metrics),status='active',severity=severity_label(mean_score),peak_temperature_c=max(o.temperature_c for o in obs),mean_anomaly_c=sum(anomalies)/len(anomalies) if anomalies else 0,max_persistence_hours=max(m.persistence_hours for m in metrics),cell_count=len(metrics),geometry=from_shape(merged,srid=4326),confidence=sum(m.confidence for m in metrics)/len(metrics),metadata_json={'metric_ids':[m.id for m in metrics],'mean_severity_score':round(mean_score,3),'method':'deterministic-threshold-cluster-v1'}); db.add(row); db.commit(); db.refresh(row); return row
