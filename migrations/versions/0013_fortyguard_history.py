"""Provider operational baseline and stress analytics."""
from alembic import op
import sqlalchemy as sa
revision="0013_fg_hist"
down_revision="0012_fg_live"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "provider_thermal_baselines",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("cell_id",sa.String(64),nullable=False),
        sa.Column("local_hour",sa.Integer(),nullable=False),
        sa.Column("sample_days",sa.Integer(),nullable=False),
        sa.Column("mean_c",sa.Float(),nullable=False),
        sa.Column("median_c",sa.Float(),nullable=False),
        sa.Column("std_c",sa.Float(),nullable=False),
        sa.Column("min_c",sa.Float(),nullable=False),
        sa.Column("max_c",sa.Float(),nullable=False),
        sa.Column("current_c",sa.Float(),nullable=False),
        sa.Column("anomaly_c",sa.Float(),nullable=False),
        sa.Column("z_score",sa.Float(),nullable=True),
        sa.Column("confidence",sa.Float(),nullable=False),
        sa.Column("truth_category",sa.String(32),nullable=False),
        sa.Column("source_activity_ids",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_table(
        "provider_thermal_stress",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("cell_id",sa.String(64),nullable=False),
        sa.Column("period_date",sa.Date(),nullable=False),
        sa.Column("threshold_c",sa.Float(),nullable=False),
        sa.Column("persistence_hours",sa.Float(),nullable=False),
        sa.Column("exceedance_hours",sa.Float(),nullable=False),
        sa.Column("truth_category",sa.String(32),nullable=False),
        sa.Column("confidence",sa.Float(),nullable=False),
        sa.Column("activity_ids",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_provider_baseline_cell_hour","provider_thermal_baselines",["cell_id","local_hour"])
    op.create_index("ix_provider_stress_cell_date","provider_thermal_stress",["cell_id","period_date"])

def downgrade():
    op.drop_index("ix_provider_stress_cell_date",table_name="provider_thermal_stress")
    op.drop_index("ix_provider_baseline_cell_hour",table_name="provider_thermal_baselines")
    op.drop_table("provider_thermal_stress")
    op.drop_table("provider_thermal_baselines")
