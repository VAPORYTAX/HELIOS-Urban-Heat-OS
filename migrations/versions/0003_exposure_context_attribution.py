"""Exposure, vulnerability, urban context, TEU and driver attribution."""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0003_exposure_core"
down_revision = "0002_thermal_core"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "urban_context_cells",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cell_id", sa.String(64), sa.ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("population", sa.Float(), nullable=False, server_default="0"),
        sa.Column("population_density_km2", sa.Float(), nullable=False, server_default="0"),
        sa.Column("vulnerable_population", sa.Float(), nullable=False, server_default="0"),
        sa.Column("vulnerability_index", sa.Float(), nullable=False, server_default="0"),
        sa.Column("vegetation_fraction", sa.Float(), nullable=True),
        sa.Column("impervious_fraction", sa.Float(), nullable=True),
        sa.Column("building_fraction", sa.Float(), nullable=True),
        sa.Column("water_fraction", sa.Float(), nullable=True),
        sa.Column("shade_fraction", sa.Float(), nullable=True),
        sa.Column("road_fraction", sa.Float(), nullable=True),
        sa.Column("solar_exposure_index", sa.Float(), nullable=True),
        sa.Column("nighttime_retention_index", sa.Float(), nullable=True),
        sa.Column("data_quality", sa.Float(), nullable=False, server_default="0"),
        sa.Column("source_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "facilities",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("area_id", sa.String(64), sa.ForeignKey("areas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("facility_type", sa.String(64), nullable=False),
        sa.Column("vulnerability_weight", sa.Float(), nullable=False, server_default="1"),
        sa.Column("capacity", sa.Float(), nullable=True),
        sa.Column("geometry", Geometry("POINT", srid=4326), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_facilities_area_type", "facilities", ["area_id", "facility_type"])

    op.create_table(
        "exposure_metrics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cell_id", sa.String(64), sa.ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hazard_index", sa.Float(), nullable=False),
        sa.Column("exposure_index", sa.Float(), nullable=False),
        sa.Column("vulnerability_index", sa.Float(), nullable=False),
        sa.Column("teu", sa.Float(), nullable=False),
        sa.Column("vulnerable_teu", sa.Float(), nullable=False),
        sa.Column("population_exposed", sa.Float(), nullable=False),
        sa.Column("vulnerable_population_exposed", sa.Float(), nullable=False),
        sa.Column("facility_exposure_score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("components_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("cell_id", "observed_at", name="uq_exposure_metric"),
    )
    op.create_index("ix_exposure_cell_time", "exposure_metrics", ["cell_id", "observed_at"])

    op.create_table(
        "driver_attributions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cell_id", sa.String(64), sa.ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dominant_driver", sa.String(64), nullable=False),
        sa.Column("driver_scores_json", sa.JSON(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("method_version", sa.String(64), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("cell_id", "observed_at", name="uq_driver_attribution"),
    )
    op.create_index("ix_driver_cell_time", "driver_attributions", ["cell_id", "observed_at"])

def downgrade():
    op.drop_index("ix_driver_cell_time", table_name="driver_attributions")
    op.drop_table("driver_attributions")
    op.drop_index("ix_exposure_cell_time", table_name="exposure_metrics")
    op.drop_table("exposure_metrics")
    op.drop_index("ix_facilities_area_type", table_name="facilities")
    op.drop_table("facilities")
    op.drop_table("urban_context_cells")

