from fastapi import APIRouter,Depends,HTTPException,Query
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from sqlalchemy import desc,select
from sqlalchemy.orm import Session
from app.db.models_thermal import ThermalCell,ThermalHotspot,ThermalMetric,ThermalObservation
from app.db.session import get_db
from app.thermal.schemas import ThermalCellIn,ThermalObservationIn
from app.thermal.service import upsert_cell,ingest_observation,rebuild_baseline_for_cell,compute_metric_for_observation,detect_hotspot
router=APIRouter(prefix='/thermal',tags=['thermal'])
@router.post('/cells')
def create_cell(body:ThermalCellIn,db:Session=Depends(get_db)):
    r=upsert_cell(db,body); return {'id':r.id,'area_id':r.area_id,'resolution_m':r.resolution_m}
@router.post('/ingest')
def ingest(body:ThermalObservationIn,db:Session=Depends(get_db)):
    if db.get(ThermalCell,body.cell_id) is None:raise HTTPException(404,detail='thermal cell not found')
    r=ingest_observation(db,body); return {'id':r.id,'cell_id':r.cell_id,'observed_at':r.observed_at}
@router.post('/baseline/{cell_id}/rebuild')
def baseline(cell_id:str,db:Session=Depends(get_db)):
    return {'cell_id':cell_id,'baseline_buckets':len(rebuild_baseline_for_cell(db,cell_id))}
@router.post('/metrics/{observation_id}/compute')
def metric(observation_id:str,threshold_c:float=Query(40),db:Session=Depends(get_db)):
    o=db.get(ThermalObservation,observation_id)
    if o is None:raise HTTPException(404,detail='observation not found')
    r=compute_metric_for_observation(db,o,threshold_c); return {'id':r.id,'cell_id':r.cell_id,'observed_at':r.observed_at,'anomaly_c':r.anomaly_c,'z_score':r.z_score,'exceedance_c':r.exceedance_c,'persistence_hours':r.persistence_hours,'severity_score':r.severity_score,'confidence':r.confidence,'components':r.components_json}
@router.get('/current')
def current(area_id:str,db:Session=Depends(get_db)):
    feats=[]
    for c in db.execute(select(ThermalCell).where(ThermalCell.area_id==area_id)).scalars().all():
      o=db.execute(select(ThermalObservation).where(ThermalObservation.cell_id==c.id).order_by(desc(ThermalObservation.observed_at)).limit(1)).scalar_one_or_none(); m=db.execute(select(ThermalMetric).where(ThermalMetric.cell_id==c.id).order_by(desc(ThermalMetric.observed_at)).limit(1)).scalar_one_or_none()
      if o: feats.append({'type':'Feature','geometry':mapping(to_shape(c.geometry)),'properties':{'cell_id':c.id,'observed_at':o.observed_at.isoformat(),'temperature_c':o.temperature_c,'source_type':o.source_type,'anomaly_c':m.anomaly_c if m else None,'persistence_hours':m.persistence_hours if m else 0,'severity_score':m.severity_score if m else None,'confidence':m.confidence if m else None}})
    return {'type':'FeatureCollection','features':feats}
@router.get('/history')
def history(cell_id:str,limit:int=Query(100,ge=1,le=5000),db:Session=Depends(get_db)):
    rows=db.execute(select(ThermalObservation).where(ThermalObservation.cell_id==cell_id).order_by(desc(ThermalObservation.observed_at)).limit(limit)).scalars().all(); return [{'id':r.id,'observed_at':r.observed_at,'temperature_c':r.temperature_c,'apparent_temperature_c':r.apparent_temperature_c,'humidity_pct':r.humidity_pct,'heat_index_c':r.heat_index_c,'source_type':r.source_type,'source_name':r.source_name} for r in rows]
@router.post('/hotspots/detect')
def hd(area_id:str,min_score:float=Query(40,ge=0,le=100),db:Session=Depends(get_db)):
    r=detect_hotspot(db,area_id,min_score); return {'detected':False} if r is None else {'detected':True,'hotspot_id':r.id,'severity':r.severity,'peak_temperature_c':r.peak_temperature_c,'mean_anomaly_c':r.mean_anomaly_c,'max_persistence_hours':r.max_persistence_hours,'cell_count':r.cell_count,'confidence':r.confidence}
@router.get('/hotspots')
def hs(area_id:str,db:Session=Depends(get_db)):
    rows=db.execute(select(ThermalHotspot).where(ThermalHotspot.area_id==area_id).order_by(desc(ThermalHotspot.detected_at))).scalars().all(); return [{'id':r.id,'detected_at':r.detected_at,'status':r.status,'severity':r.severity,'peak_temperature_c':r.peak_temperature_c,'mean_anomaly_c':r.mean_anomaly_c,'max_persistence_hours':r.max_persistence_hours,'cell_count':r.cell_count,'confidence':r.confidence} for r in rows]
@router.get('/hotspots/{hotspot_id}')
def h(hotspot_id:str,db:Session=Depends(get_db)):
    r=db.get(ThermalHotspot,hotspot_id)
    if r is None:raise HTTPException(404,detail='hotspot not found')
    return {'id':r.id,'area_id':r.area_id,'detected_at':r.detected_at,'status':r.status,'severity':r.severity,'peak_temperature_c':r.peak_temperature_c,'mean_anomaly_c':r.mean_anomaly_c,'max_persistence_hours':r.max_persistence_hours,'cell_count':r.cell_count,'confidence':r.confidence,'geometry':mapping(to_shape(r.geometry)),'metadata':r.metadata_json}
