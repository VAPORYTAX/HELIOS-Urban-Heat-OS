"""Census ACS demographic lineage and cell allocation."""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0008_demographics"
down_revision = "0007_realdata"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "census_tract_demographics",
        sa.Column("geoid", sa.String(16), primary_key=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("state_fips", sa.String(2), nullable=False),
        sa.Column("county_fips", sa.String(3), nullable=False),
        sa.Column("tract_code", sa.String(6), nullable=False),
        sa.Column("geometry", Geometry("MULTIPOLYGON", srid=4326), nullable=False),
        sa.Column("population", sa.Float(), nullable=False),
        sa.Column("population_moe", sa.Float(), nullable=True),
        sa.Column("under5_population", sa.Float(), nullable=False),
        sa.Column("age65_population", sa.Float(), nullable=False),
        sa.Column("poverty_universe", sa.Float(), nullable=False),
        sa.Column("poverty_population", sa.Float(), nullable=False),
        sa.Column("households", sa.Float(), nullable=False),
        sa.Column("no_vehicle_households", sa.Float(), nullable=False),
        sa.Column("source_year", sa.Integer(), nullable=False),
        sa.Column("source_dataset", sa.String(64), nullable=False),
        sa.Column("variables_json", sa.JSON(), nullable=False),
        sa.Column("quality_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_census_tract_geom", "census_tract_demographics", ["geometry"], postgresql_using="gist")

    op.create_table(
        "cell_demographics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cell_id", sa.String(64), sa.ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("population", sa.Float(), nullable=False),
        sa.Column("population_density_km2", sa.Float(), nullable=False),
        sa.Column("under5_population", sa.Float(), nullable=False),
        sa.Column("age65_population", sa.Float(), nullable=False),
        sa.Column("poverty_population", sa.Float(), nullable=False),
        sa.Column("no_vehicle_households", sa.Float(), nullable=False),
        sa.Column("vulnerability_index", sa.Float(), nullable=False),
        sa.Column("derived_vulnerable_population", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("allocation_json", sa.JSON(), nullable=False),
        sa.Column("source_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table("cell_demographics")
    op.drop_index("ix_census_tract_geom", table_name="census_tract_demographics")
    op.drop_table("census_tract_demographics")
