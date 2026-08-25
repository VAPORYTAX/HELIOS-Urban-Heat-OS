"""Gemma intelligence gateway runs and validation ledger."""
from alembic import op
import sqlalchemy as sa

revision = "0011_intelligence"
down_revision = "0010_contextforge"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "intelligence_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("context_packet_id", sa.String(36), sa.ForeignKey("context_packets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("area_id", sa.String(64), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(256), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("thinking_enabled", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=False),
        sa.Column("response_json", sa.JSON(), nullable=False),
        sa.Column("validation_json", sa.JSON(), nullable=False),
        sa.Column("fallback_used", sa.Boolean(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_intel_area_created", "intelligence_runs", ["area_id", "created_at"])

def downgrade():
    op.drop_index("ix_intel_area_created", table_name="intelligence_runs")
    op.drop_table("intelligence_runs")
