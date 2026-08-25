from datetime import datetime, timezone
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class City(Base):
    __tablename__ = "cities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    boundary = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ProviderActivity(Base):
    __tablename__ = "provider_activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    activity_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    operation: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    request_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    source_operation: Mapped[str] = mapped_column(String(128), nullable=False)
    source_activity_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    quality_label: Mapped[str] = mapped_column(String(32), nullable=False, default="provider")
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

from app.db.models_thermal import Area, ThermalCell, ThermalObservation, ThermalBaseline, ThermalMetric, ThermalHotspot, ThermalEvent  # noqa: F401

from app.db.models_exposure import UrbanContextCell, Facility, ExposureMetric, DriverAttribution  # noqa: F401

from app.db.models_interventions import InterventionCatalog, InterventionCandidate, Scenario, ScenarioIntervention, ScenarioResult  # noqa: F401

from app.db.models_optimizer import OptimizationRun, OptimizationSelection  # noqa: F401

from app.db.models_agents import AgentRun, AgentFinding, EvidenceRecord, Recommendation  # noqa: F401

from app.db.models_realdata import DataSyncRun  # noqa: F401

from app.db.models_demographics import CensusTractDemographic, CellDemographic  # noqa: F401

from app.db.models_quality import SystemAuditEvent, QualitySnapshot  # noqa: F401

from app.db.models_context import PromptRegistry, ContextPacket  # noqa: F401

from app.db.models_intelligence import IntelligenceRun  # noqa: F401

from app.db.models_fortyguard import FortyGuardIngestRun  # noqa: F401

from app.db.models_provider_history import ProviderThermalBaseline, ProviderThermalStress  # noqa: F401\n\nfrom app.db.models_fortyguard_checkpoint import FortyGuardHistoryCheckpoint  # noqa: F401\n

from app.db.models_provider_ops import ProviderOperationalMetric  # noqa: F401\n

from app.db.models_provider_decision import ProviderInterventionCandidate, ProviderOptimizerRun, ProviderAgentDecision  # noqa: F401\n\nfrom app.db.models_decision_science import DecisionScienceRun, ThermalWayNetworkAudit  # noqa: F401\n

from app.db.models_thermalway import ThermalWayOSMNode, ThermalWayOSMEdge, ThermalWayRouteRun  # noqa: F401\n\nfrom app.db.models_thermalway_intel import ThermalWayCorridorScore  # noqa: F401\n

from app.db.models_thermalway_access import ThermalWayAccessibilityScore, ThermalWayCriticalJourney  # noqa: F401
