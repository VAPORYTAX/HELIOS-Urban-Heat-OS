from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import DateTime,Float,Integer,JSON,String
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)

class ThermalWayCorridorScore(Base):
    __tablename__="thermalway_corridor_scores"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    edge_id: Mapped[str]=mapped_column(String(64),nullable=False)
    thermal_cost: Mapped[float]=mapped_column(Float,nullable=False)
    vulnerable_thermal_cost: Mapped[float]=mapped_column(Float,nullable=False)
    route_frequency: Mapped[int]=mapped_column(Integer,nullable=False)
    investment_priority: Mapped[float]=mapped_column(Float,nullable=False)
    recommended_intervention: Mapped[str]=mapped_column(String(64),nullable=False)
    evidence_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
