from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import JSON,Boolean,DateTime,Float,String
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base
def utcnow(): return datetime.now(timezone.utc)

class ProviderInterventionCandidate(Base):
    __tablename__="provider_intervention_candidates"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    run_id: Mapped[str]=mapped_column(String(36),nullable=False)
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    cell_id: Mapped[str]=mapped_column(String(64),nullable=False)
    intervention_type: Mapped[str]=mapped_column(String(64),nullable=False)
    cost: Mapped[float]=mapped_column(Float,nullable=False)
    temperature_delta_c: Mapped[float]=mapped_column(Float,nullable=False)
    teu_reduction: Mapped[float]=mapped_column(Float,nullable=False)
    va_teu_reduction: Mapped[float]=mapped_column(Float,nullable=False)
    people_benefit_proxy: Mapped[float]=mapped_column(Float,nullable=False)
    feasibility: Mapped[float]=mapped_column(Float,nullable=False)
    confidence: Mapped[float]=mapped_column(Float,nullable=False)
    assumption_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)

class ProviderOptimizerRun(Base):
    __tablename__="provider_optimizer_runs"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    budget: Mapped[float]=mapped_column(Float,nullable=False)
    objective: Mapped[str]=mapped_column(String(64),nullable=False)
    status: Mapped[str]=mapped_column(String(32),nullable=False)
    selected_json: Mapped[list]=mapped_column(JSON,nullable=False)
    total_cost: Mapped[float]=mapped_column(Float,nullable=False)
    teu_reduction: Mapped[float]=mapped_column(Float,nullable=False)
    va_teu_reduction: Mapped[float]=mapped_column(Float,nullable=False)
    confidence: Mapped[float]=mapped_column(Float,nullable=False)
    source_metric_ids: Mapped[list]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)

class ProviderAgentDecision(Base):
    __tablename__="provider_agent_decisions"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid4()))
    optimizer_run_id: Mapped[str]=mapped_column(String(36),nullable=False)
    area_id: Mapped[str]=mapped_column(String(64),nullable=False)
    status: Mapped[str]=mapped_column(String(32),nullable=False)
    confidence: Mapped[float]=mapped_column(Float,nullable=False)
    requires_human_review: Mapped[bool]=mapped_column(Boolean,nullable=False)
    agent_actions_json: Mapped[list]=mapped_column(JSON,nullable=False)
    evidence_json: Mapped[dict]=mapped_column(JSON,nullable=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
