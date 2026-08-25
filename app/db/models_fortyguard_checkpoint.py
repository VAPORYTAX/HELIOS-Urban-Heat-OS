from datetime import datetime, timezone, date
from uuid import uuid4
from sqlalchemy import JSON, Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def utcnow(): return datetime.now(timezone.utc)

class FortyGuardHistoryCheckpoint(Base):
    __tablename__="fortyguard_history_checkpoints"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    request_key: Mapped[str]=mapped_column(String(160),nullable=False,unique=True)
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    request_kind: Mapped[str]=mapped_column(String(32),nullable=False)
    request_date: Mapped[date|None]=mapped_column(Date,nullable=True)
    activity_id: Mapped[str|None]=mapped_column(String(64),nullable=True)
    state: Mapped[str]=mapped_column(String(32),nullable=False)
    payload_json: Mapped[dict]=mapped_column(JSON,nullable=False,default=dict)
    result_json: Mapped[dict]=mapped_column(JSON,nullable=False,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
