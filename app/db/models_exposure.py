from datetime import datetime, timezone
from uuid import uuid4

from geoalchemy2 import Geometry
from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class UrbanContextCell(Base):
    __tablename__ = "urban_context_cells"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    cell_id: Mapped[str] = mapped_column(String(64), ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False, unique=True)
    population: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    population_density_km2: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vulnerable_population: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vulnerability_index: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    vegetation_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    impervious_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    building_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    shade_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    road_fraction: Mapped[float | None] = mapped_column(Float, nullable=True)
    solar_exposure_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    nighttime_retention_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    data_quality: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Facility(Base):
    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    area_id: Mapped[str] = mapped_column(String(64), ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    facility_type: Mapped[str] = mapped_column(String(64), nullable=False)
    vulnerability_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    capacity: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ExposureMetric(Base):
    __tablename__ = "exposure_metrics"
    __table_args__ = (UniqueConstraint("cell_id", "observed_at", name="uq_exposure_metric"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    cell_id: Mapped[str] = mapped_column(String(64), ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    hazard_index: Mapped[float] = mapped_column(Float, nullable=False)
    exposure_index: Mapped[float] = mapped_column(Float, nullable=False)
    vulnerability_index: Mapped[float] = mapped_column(Float, nullable=False)
    teu: Mapped[float] = mapped_column(Float, nullable=False)
    vulnerable_teu: Mapped[float] = mapped_column(Float, nullable=False)
    population_exposed: Mapped[float] = mapped_column(Float, nullable=False)
    vulnerable_population_exposed: Mapped[float] = mapped_column(Float, nullable=False)
    facility_exposure_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    components_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class DriverAttribution(Base):
    __tablename__ = "driver_attributions"
    __table_args__ = (UniqueConstraint("cell_id", "observed_at", name="uq_driver_attribution"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    cell_id: Mapped[str] = mapped_column(String(64), ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dominant_driver: Mapped[str] = mapped_column(String(64), nullable=False)
    driver_scores_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    method_version: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
