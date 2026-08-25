from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)
class FortyGuardIngestRun(Base):
    __tablename__="fortyguard_ingest_runs"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    activity_id: Mapped[str]=mapped_column(String(64),nullable=False,unique=True)
    status: Mapped[str]=mapped_column(String(32),nullable=False)
    target_time: Mapped[datetime]=mapped_column(DateTime(timezone=True),nullable=False)
    granularity_m: Mapped[int]=mapped_column(Integer,nullable=False)
    analytic_type: Mapped[str]=mapped_column(String(32),nullable=False)
    tile_count: Mapped[int]=mapped_column(Integer,nullable=False)
    cells_updated: Mapped[int]=mapped_column(Integer,nullable=False)
    stats_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    mapping_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    completed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
