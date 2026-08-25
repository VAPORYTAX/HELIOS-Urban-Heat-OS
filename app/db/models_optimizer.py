from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    area_id: Mapped[str] = mapped_column(String(64), ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)
    scenario_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True)
    objective: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")
    budget: Mapped[float] = mapped_column(Float, nullable=False)
    min_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_implementation_months: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_interventions_per_cell: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    min_vulnerable_benefit_share: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    objective_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    selected_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    solver_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class OptimizationSelection(Base):
    __tablename__ = "optimization_selections"
    __table_args__ = (UniqueConstraint("run_id", "candidate_id", name="uq_opt_run_candidate"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("optimization_runs.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("intervention_candidates.id", ondelete="CASCADE"), nullable=False)
    cell_id: Mapped[str] = mapped_column(String(64), nullable=False)
    intervention_id: Mapped[str] = mapped_column(String(64), nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_teu_benefit: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_vulnerable_teu_benefit: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_people_benefit: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    score_components_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
