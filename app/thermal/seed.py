from datetime import datetime,timezone
from geoalchemy2.shape import from_shape
from shapely.geometry import MultiPolygon,Polygon
from sqlalchemy import delete,select
from app.db.models import City
from app.db.models_thermal import Area,ThermalBaseline,ThermalCell,ThermalHotspot,ThermalMetric,ThermalObservation
from app.db.session import SessionLocal
from app.thermal.fixture import fixture_grid,fixture_observations
from app.thermal.schemas import ThermalCellIn,ThermalObservationIn
from app.thermal.service import upsert_cell,ingest_observation,rebuild_baseline_for_cell,compute_metric_for_observation,detect_hotspot
def seed(reset=False):
 db=SessionLocal()
 try:
  if reset:
   for model in (ThermalHotspot,ThermalMetric,ThermalBaseline,ThermalObservation,ThermalCell): db.execute(delete(model))
   db.execute(delete(Area).where(Area.id=='phx-downtown')); db.execute(delete(City).where(City.id=='phoenix')); db.commit()
  if db.get(City,'phoenix') is None: db.add(City(id='phoenix',name='Phoenix',country_code='US',timezone='America/Phoenix',created_at=datetime.now(timezone.utc))); db.commit()
  if db.get(Area,'phx-downtown') is None:
   ring=[(-112.0785,33.4455),(-112.0655,33.4455),(-112.0655,33.4555),(-112.0785,33.4555),(-112.0785,33.4455)]; db.add(Area(id='phx-downtown',city_id='phoenix',name='Downtown Phoenix Starter Area',area_type='aoi',geometry=from_shape(MultiPolygon([Polygon(ring)]),srid=4326),created_at=datetime.now(timezone.utc))); db.commit()
  for c in fixture_grid(): upsert_cell(db,ThermalCellIn(**c))
  for x in fixture_observations(): ingest_observation(db,ThermalObservationIn(**x))
  ids=db.execute(select(ThermalCell.id).where(ThermalCell.area_id=='phx-downtown')).scalars().all()
  for cid in ids: rebuild_baseline_for_cell(db,cid,3)
  obs=db.execute(select(ThermalObservation).where(ThermalObservation.cell_id.in_(ids))).scalars().all()
  for o in obs: compute_metric_for_observation(db,o,40)
  hot=detect_hotspot(db,'phx-downtown',40); return {'city':'phoenix','area':'phx-downtown','cells':len(ids),'observations':len(obs),'hotspot_id':hot.id if hot else None}
 finally: db.close()
