from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import BigInteger,DateTime,Float,JSON,String
from sqlalchemy.orm import Mapped,mapped_column
from geoalchemy2 import Geometry
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)

class ThermalWayOSMNode(Base):
    __tablename__="thermalway_osm_nodes"
    osm_node_id: Mapped[int]=mapped_column(BigInteger,primary_key=True)
    geometry=mapped_column(Geometry("POINT",srid=4326),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)

class ThermalWayOSMEdge(Base):
    __tablename__="thermalway_osm_edges"
    id: Mapped[str]=mapped_column(String(64),primary_key=True)
    osm_way_id: Mapped[int]=mapped_column(BigInteger,nullable=False)
    u: Mapped[int]=mapped_column(BigInteger,nullable=False)
    v: Mapped[int]=mapped_column(BigInteger,nullable=False)
    geometry=mapped_column(Geometry("LINESTRING",srid=4326),nullable=False)
    length_m: Mapped[float]=mapped_column(Float,nullable=False)
    highway: Mapped[str|None]=mapped_column(String(64))
    name: Mapped[str|None]=mapped_column(String(256))
    foot: Mapped[str|None]=mapped_column(String(64))
    sidewalk: Mapped[str|None]=mapped_column(String(64))
    covered: Mapped[str|None]=mapped_column(String(32))
    access: Mapped[str|None]=mapped_column(String(64))
    tags_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    source: Mapped[str]=mapped_column(String(64),nullable=False)
    source_timestamp: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)

class ThermalWayRouteRun(Base):
    __tablename__="thermalway_route_runs"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    mode: Mapped[str]=mapped_column(String(32),nullable=False)
    traveler_profile: Mapped[str]=mapped_column(String(64),nullable=False)
    origin_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    destination_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    route_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    distance_m: Mapped[float]=mapped_column(Float,nullable=False)
    duration_min: Mapped[float]=mapped_column(Float,nullable=False)
    thermal_exposure_cost: Mapped[float]=mapped_column(Float,nullable=False)
    confidence: Mapped[float]=mapped_column(Float,nullable=False)
    truth_category: Mapped[str]=mapped_column(String(64),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
