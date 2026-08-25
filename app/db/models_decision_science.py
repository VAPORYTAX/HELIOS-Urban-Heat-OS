from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import JSON,Boolean,DateTime,Float,Integer,String
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)

class DecisionScienceRun(Base):
    __tablename__="decision_science_runs"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    optimizer_run_id: Mapped[str]=mapped_column(String(36),nullable=False)
    status: Mapped[str]=mapped_column(String(32),nullable=False)
    robustness_score: Mapped[float]=mapped_column(Float,nullable=False)
    max_regret: Mapped[float]=mapped_column(Float,nullable=False)
    mean_regret: Mapped[float]=mapped_column(Float,nullable=False)
    sensitivity_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    voi_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    reverse_optimization_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    sequencing_json: Mapped[list]=mapped_column(JSON,nullable=False)
    what_changes_mind_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)

class ThermalWayNetworkAudit(Base):
    __tablename__="thermalway_network_audits"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    status: Mapped[str]=mapped_column(String(32),nullable=False)
    source_table: Mapped[str|None]=mapped_column(String(128),nullable=True)
    geometry_column: Mapped[str|None]=mapped_column(String(128),nullable=True)
    candidate_tables_json: Mapped[list]=mapped_column(JSON,nullable=False)
    line_feature_count: Mapped[int]=mapped_column(Integer,nullable=False)
    real_osm_network_proven: Mapped[bool]=mapped_column(Boolean,nullable=False)
    notes_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
