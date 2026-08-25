"""External real-data synchronization ledger."""
from alembic import op
import sqlalchemy as sa

revision = "0007_realdata"
down_revision = "0006_agents"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "data_sync_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("area_id", sa.String(64), sa.ForeignKey("areas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("truth_category", sa.String(32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_received", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_applied", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("details_json", sa.JSON(), nullable=False),
        sa.Column("error_text", sa.Text(), nullable=True),
    )
    op.create_index("ix_sync_area_provider", "data_sync_runs", ["area_id", "provider"])

def downgrade():
    op.drop_index("ix_sync_area_provider", table_name="data_sync_runs")
    op.drop_table("data_sync_runs")
