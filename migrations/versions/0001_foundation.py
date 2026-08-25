"""HELIOS foundation tables."""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "cities",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("boundary", Geometry("MULTIPOLYGON", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "provider_activities",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("activity_id", sa.String(128), nullable=False, unique=True),
        sa.Column("operation", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=True),
        sa.Column("error_json", sa.JSON(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "provenance_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("source_operation", sa.String(128), nullable=False),
        sa.Column("source_activity_id", sa.String(128), nullable=True),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_version", sa.String(64), nullable=True),
        sa.Column("quality_label", sa.String(32), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )

    op.create_index(
        "ix_provenance_entity",
        "provenance_records",
        ["entity_type", "entity_id"],
    )

def downgrade():
    op.drop_index("ix_provenance_entity", table_name="provenance_records")
    op.drop_table("provenance_records")
    op.drop_table("provider_activities")
    op.drop_table("cities")
