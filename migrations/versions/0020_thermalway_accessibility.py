from alembic import op
import sqlalchemy as sa
revision="0020_tw_access"
down_revision="0019_thermalway_intel"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("thermalway_accessibility_scores",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("cell_id",sa.String(64),nullable=False),
        sa.Column("traveler_profile",sa.String(64),nullable=False),
        sa.Column("facility_count",sa.Integer(),nullable=False),
        sa.Column("best_duration_min",sa.Float(),nullable=False),
        sa.Column("best_tec",sa.Float(),nullable=False),
        sa.Column("accessibility_score",sa.Float(),nullable=False),
        sa.Column("best_facility_json",sa.JSON(),nullable=False),
        sa.Column("truth_category",sa.String(64),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
    op.create_table("thermalway_critical_journeys",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("journey_type",sa.String(64),nullable=False),
        sa.Column("origin_cell_id",sa.String(64),nullable=False),
        sa.Column("traveler_profile",sa.String(64),nullable=False),
        sa.Column("facility_json",sa.JSON(),nullable=False),
        sa.Column("fastest_json",sa.JSON(),nullable=False),
        sa.Column("thermal_safe_json",sa.JSON(),nullable=False),
        sa.Column("thermal_cost_saved",sa.Float(),nullable=False),
        sa.Column("extra_minutes",sa.Float(),nullable=False),
        sa.Column("protection_score",sa.Float(),nullable=False),
        sa.Column("truth_category",sa.String(64),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False))
def downgrade():
    op.drop_table("thermalway_critical_journeys")
    op.drop_table("thermalway_accessibility_scores")
