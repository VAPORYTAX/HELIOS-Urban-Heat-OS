from datetime import datetime, timezone
from uuid import uuid4
from geoalchemy2 import Geometry
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class CensusTractDemographic(Base):
    __tablename__ = "census_tract_demographics"

    geoid: Mapped[str] = mapped_column(String(16), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    state_fips: Mapped[str] = mapped_column(String(2), nullable=False)
    county_fips: Mapped[str] = mapped_column(String(3), nullable=False)
    tract_code: Mapped[str] = mapped_column(String(6), nullable=False)
    geometry = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=False)
    population: Mapped[float] = mapped_column(Float, nullable=False)
    population_moe: Mapped[float | None] = mapped_column(Float, nullable=True)
    under5_population: Mapped[float] = mapped_column(Float, nullable=False)
    age65_population: Mapped[float] = mapped_column(Float, nullable=False)
    poverty_universe: Mapped[float] = mapped_column(Float, nullable=False)
    poverty_population: Mapped[float] = mapped_column(Float, nullable=False)
    households: Mapped[float] = mapped_column(Float, nullable=False)
    no_vehicle_households: Mapped[float] = mapped_column(Float, nullable=False)
    source_year: Mapped[int] = mapped_column(Integer, nullable=False)
    source_dataset: Mapped[str] = mapped_column(String(64), nullable=False)
    variables_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    quality_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class CellDemographic(Base):
    __tablename__ = "cell_demographics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    cell_id: Mapped[str] = mapped_column(String(64), ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False, unique=True)
    population: Mapped[float] = mapped_column(Float, nullable=False)
    population_density_km2: Mapped[float] = mapped_column(Float, nullable=False)
    under5_population: Mapped[float] = mapped_column(Float, nullable=False)
    age65_population: Mapped[float] = mapped_column(Float, nullable=False)
    poverty_population: Mapped[float] = mapped_column(Float, nullable=False)
    no_vehicle_households: Mapped[float] = mapped_column(Float, nullable=False)
    vulnerability_index: Mapped[float] = mapped_column(Float, nullable=False)
    derived_vulnerable_population: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    allocation_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
