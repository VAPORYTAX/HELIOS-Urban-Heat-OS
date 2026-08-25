"""Scientific and reliability hardening."""
from alembic import op
import sqlalchemy as sa

revision = "0009_hardening"
down_revision = "0008_demographics"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "system_audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("area_id", sa.String(64), nullable=True),
        sa.Column("entity_type", sa.String(64), nullable=True),
        sa.Column("entity_id", sa.String(128), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_type_created", "system_audit_events", ["event_type", "created_at"])

    op.create_table(
        "quality_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("area_id", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("health_score", sa.Float(), nullable=False),
        sa.Column("requires_human_review", sa.Boolean(), nullable=False),
        sa.Column("checks_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_quality_area_created", "quality_snapshots", ["area_id", "created_at"])

def downgrade():
    op.drop_index("ix_quality_area_created", table_name="quality_snapshots")
    op.drop_table("quality_snapshots")
    op.drop_index("ix_audit_type_created", table_name="system_audit_events")
    op.drop_table("system_audit_events")
