from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import DateTime,Float,Integer,JSON,String
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)
class ThermalWayAccessibilityScore(Base):
    __tablename__="thermalway_accessibility_scores"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    cell_id: Mapped[str]=mapped_column(String(64),nullable=False)
    traveler_profile: Mapped[str]=mapped_column(String(64),nullable=False)
    facility_count: Mapped[int]=mapped_column(Integer,nullable=False)
    best_duration_min: Mapped[float]=mapped_column(Float,nullable=False)
    best_tec: Mapped[float]=mapped_column(Float,nullable=False)
    accessibility_score: Mapped[float]=mapped_column(Float,nullable=False)
    best_facility_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    truth_category: Mapped[str]=mapped_column(String(64),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
class ThermalWayCriticalJourney(Base):
    __tablename__="thermalway_critical_journeys"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    journey_type: Mapped[str]=mapped_column(String(64),nullable=False)
    origin_cell_id: Mapped[str]=mapped_column(String(64),nullable=False)
    traveler_profile: Mapped[str]=mapped_column(String(64),nullable=False)
    facility_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    fastest_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    thermal_safe_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    thermal_cost_saved: Mapped[float]=mapped_column(Float,nullable=False)
    extra_minutes: Mapped[float]=mapped_column(Float,nullable=False)
    protection_score: Mapped[float]=mapped_column(Float,nullable=False)
    truth_category: Mapped[str]=mapped_column(String(64),nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
