from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import JSON,DateTime,Float,String
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)
class ProviderOperationalMetric(Base):
    __tablename__="provider_operational_metrics"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    cell_id: Mapped[str]=mapped_column(String(64),nullable=False)
    current_c: Mapped[float]=mapped_column(Float,nullable=False)
    baseline_mean_c: Mapped[float]=mapped_column(Float,nullable=False)
    anomaly_c: Mapped[float]=mapped_column(Float,nullable=False)
    z_score: Mapped[float|None]=mapped_column(Float,nullable=True)
    persistence_hours: Mapped[float|None]=mapped_column(Float,nullable=True)
    exceedance_hours: Mapped[float|None]=mapped_column(Float,nullable=True)
    temperature_stress: Mapped[float]=mapped_column(Float,nullable=False)
    anomaly_stress: Mapped[float]=mapped_column(Float,nullable=False)
    persistence_stress: Mapped[float]=mapped_column(Float,nullable=False)
    exceedance_stress: Mapped[float]=mapped_column(Float,nullable=False)
    hazard_index: Mapped[float]=mapped_column(Float,nullable=False)
    severity: Mapped[str]=mapped_column(String(32),nullable=False)
    population: Mapped[float]=mapped_column(Float,nullable=False)
    vulnerability_index: Mapped[float]=mapped_column(Float,nullable=False)
    teu: Mapped[float]=mapped_column(Float,nullable=False)
    va_teu: Mapped[float]=mapped_column(Float,nullable=False)
    confidence: Mapped[float]=mapped_column(Float,nullable=False)
    truth_category: Mapped[str]=mapped_column(String(32),nullable=False)
    model_version: Mapped[str]=mapped_column(String(64),nullable=False)
    evidence_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
