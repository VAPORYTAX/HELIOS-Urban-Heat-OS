"""Provider operational hazard and burden metrics."""
from alembic import op
import sqlalchemy as sa
revision="0015_provider_ops"
down_revision="0014_fg_ckpt"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "provider_operational_metrics",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("cell_id",sa.String(64),nullable=False),
        sa.Column("current_c",sa.Float(),nullable=False),
        sa.Column("baseline_mean_c",sa.Float(),nullable=False),
        sa.Column("anomaly_c",sa.Float(),nullable=False),
        sa.Column("z_score",sa.Float(),nullable=True),
        sa.Column("persistence_hours",sa.Float(),nullable=True),
        sa.Column("exceedance_hours",sa.Float(),nullable=True),
        sa.Column("temperature_stress",sa.Float(),nullable=False),
        sa.Column("anomaly_stress",sa.Float(),nullable=False),
        sa.Column("persistence_stress",sa.Float(),nullable=False),
        sa.Column("exceedance_stress",sa.Float(),nullable=False),
        sa.Column("hazard_index",sa.Float(),nullable=False),
        sa.Column("severity",sa.String(32),nullable=False),
        sa.Column("population",sa.Float(),nullable=False),
        sa.Column("vulnerability_index",sa.Float(),nullable=False),
        sa.Column("teu",sa.Float(),nullable=False),
        sa.Column("va_teu",sa.Float(),nullable=False),
        sa.Column("confidence",sa.Float(),nullable=False),
        sa.Column("truth_category",sa.String(32),nullable=False),
        sa.Column("model_version",sa.String(64),nullable=False),
        sa.Column("evidence_json",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_provider_ops_area_cell","provider_operational_metrics",["area_id","cell_id"])

def downgrade():
    op.drop_index("ix_provider_ops_area_cell",table_name="provider_operational_metrics")
    op.drop_table("provider_operational_metrics")
