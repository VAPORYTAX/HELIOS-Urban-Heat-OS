"""FortyGuard live provider provenance."""
from alembic import op
import sqlalchemy as sa
revision="0012_fg_live"
down_revision="0011_intelligence"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table(
        "fortyguard_ingest_runs",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("activity_id",sa.String(64),nullable=False,unique=True),
        sa.Column("status",sa.String(32),nullable=False),
        sa.Column("target_time",sa.DateTime(timezone=True),nullable=False),
        sa.Column("granularity_m",sa.Integer(),nullable=False),
        sa.Column("analytic_type",sa.String(32),nullable=False),
        sa.Column("tile_count",sa.Integer(),nullable=False),
        sa.Column("cells_updated",sa.Integer(),nullable=False),
        sa.Column("stats_json",sa.JSON(),nullable=False),
        sa.Column("mapping_json",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
        sa.Column("completed_at",sa.DateTime(timezone=True),nullable=True),
    )
    op.create_index("ix_fg_ingest_area_time","fortyguard_ingest_runs",["area_id","target_time"])
def downgrade():
    op.drop_index("ix_fg_ingest_area_time",table_name="fortyguard_ingest_runs")
    op.drop_table("fortyguard_ingest_runs")
