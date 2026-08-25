from datetime import datetime, timezone, date
from uuid import uuid4
from sqlalchemy import JSON, Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)

class ProviderThermalBaseline(Base):
    __tablename__="provider_thermal_baselines"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    cell_id: Mapped[str]=mapped_column(String(64),nullable=False)
    local_hour: Mapped[int]=mapped_column(Integer,nullable=False)
    sample_days: Mapped[int]=mapped_column(Integer,nullable=False)
    mean_c: Mapped[float]=mapped_column(Float,nullable=False)
    median_c: Mapped[float]=mapped_column(Float,nullable=False)
    std_c: Mapped[float]=mapped_column(Float,nullable=False)
    min_c: Mapped[float]=mapped_column(Float,nullable=False)
    max_c: Mapped[float]=mapped_column(Float,nullable=False)
    current_c: Mapped[float]=mapped_column(Float,nullable=False)
    anomaly_c: Mapped[float]=mapped_column(Float,nullable=False)
    z_score: Mapped[float|None]=mapped_column(Float,nullable=True)
    confidence: Mapped[float]=mapped_column(Float,nullable=False)
    truth_category: Mapped[str]=mapped_column(String(32),nullable=False)
    source_activity_ids: Mapped[list]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)

class ProviderThermalStress(Base):
    __tablename__="provider_thermal_stress"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    cell_id: Mapped[str]=mapped_column(String(64),nullable=False)
    period_date: Mapped[date]=mapped_column(Date,nullable=False)
    threshold_c: Mapped[float]=mapped_column(Float,nullable=False)
    persistence_hours: Mapped[float]=mapped_column(Float,nullable=False)
    exceedance_hours: Mapped[float]=mapped_column(Float,nullable=False)
    truth_category: Mapped[str]=mapped_column(String(32),nullable=False)
    confidence: Mapped[float]=mapped_column(Float,nullable=False)
    activity_ids: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
