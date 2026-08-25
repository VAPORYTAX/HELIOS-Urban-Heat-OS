from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class InterventionCatalog(Base):
    __tablename__ = "intervention_catalog"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    effect_profile_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    cost_model_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    constraints_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    evidence_level: Mapped[str] = mapped_column(String(32), nullable=False)
    base_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class InterventionCandidate(Base):
    __tablename__ = "intervention_candidates"
    __table_args__ = (UniqueConstraint("cell_id", "intervention_id", name="uq_candidate_cell_intervention"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    cell_id: Mapped[str] = mapped_column(String(64), ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False)
    intervention_id: Mapped[str] = mapped_column(String(64), ForeignKey("intervention_catalog.id", ondelete="CASCADE"), nullable=False)
    suitability_score: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=False)
    implementation_months: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reasons_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    constraints_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    area_id: Mapped[str] = mapped_column(String(64), ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    objective: Mapped[str] = mapped_column(String(64), nullable=False, default="balanced")
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ScenarioIntervention(Base):
    __tablename__ = "scenario_interventions"
    __table_args__ = (UniqueConstraint("scenario_id", "candidate_id", name="uq_scenario_candidate"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False)
    candidate_id: Mapped[str] = mapped_column(String(36), ForeignKey("intervention_candidates.id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ScenarioResult(Base):
    __tablename__ = "scenario_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    scenario_id: Mapped[str] = mapped_column(String(36), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, unique=True)
    baseline_teu: Mapped[float] = mapped_column(Float, nullable=False)
    projected_teu: Mapped[float] = mapped_column(Float, nullable=False)
    teu_reduction: Mapped[float] = mapped_column(Float, nullable=False)
    teu_reduction_pct: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_vulnerable_teu: Mapped[float] = mapped_column(Float, nullable=False)
    projected_vulnerable_teu: Mapped[float] = mapped_column(Float, nullable=False)
    vulnerable_teu_reduction: Mapped[float] = mapped_column(Float, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    thermal_roi: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    lower_teu_reduction: Mapped[float] = mapped_column(Float, nullable=False)
    upper_teu_reduction: Mapped[float] = mapped_column(Float, nullable=False)
    assumptions_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    cell_results_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
