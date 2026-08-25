"""ThermalWay safe haven, temporal planning, and corridor intelligence."""
from alembic import op
import sqlalchemy as sa
revision="0019_thermalway_intel"
down_revision="0018_thermalway_real"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "thermalway_corridor_scores",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("edge_id",sa.String(64),nullable=False),
        sa.Column("thermal_cost",sa.Float(),nullable=False),
        sa.Column("vulnerable_thermal_cost",sa.Float(),nullable=False),
        sa.Column("route_frequency",sa.Integer(),nullable=False),
        sa.Column("investment_priority",sa.Float(),nullable=False),
        sa.Column("recommended_intervention",sa.String(64),nullable=False),
        sa.Column("evidence_json",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_tw_corridor_area_priority","thermalway_corridor_scores",["area_id","investment_priority"])

def downgrade():
    op.drop_index("ix_tw_corridor_area_priority",table_name="thermalway_corridor_scores")
    op.drop_table("thermalway_corridor_scores")
