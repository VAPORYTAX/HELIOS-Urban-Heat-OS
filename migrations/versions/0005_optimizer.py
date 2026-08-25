"""Mathematical intervention portfolio optimizer."""
from alembic import op
import sqlalchemy as sa

revision = "0005_optimizer"
down_revision = "0004_interventions"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "optimization_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("area_id", sa.String(64), sa.ForeignKey("areas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scenario_id", sa.String(36), sa.ForeignKey("scenarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("objective", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("budget", sa.Float(), nullable=False),
        sa.Column("min_confidence", sa.Float(), nullable=False),
        sa.Column("max_implementation_months", sa.Float(), nullable=True),
        sa.Column("max_interventions_per_cell", sa.Integer(), nullable=False),
        sa.Column("min_vulnerable_benefit_share", sa.Float(), nullable=False),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("objective_value", sa.Float(), nullable=True),
        sa.Column("total_cost", sa.Float(), nullable=True),
        sa.Column("selected_count", sa.Integer(), nullable=True),
        sa.Column("solver_status", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_opt_runs_area_created", "optimization_runs", ["area_id", "created_at"])

    op.create_table(
        "optimization_selections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("optimization_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_id", sa.String(36), sa.ForeignKey("intervention_candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cell_id", sa.String(64), nullable=False),
        sa.Column("intervention_id", sa.String(64), nullable=False),
        sa.Column("cost", sa.Float(), nullable=False),
        sa.Column("estimated_teu_benefit", sa.Float(), nullable=False),
        sa.Column("estimated_vulnerable_teu_benefit", sa.Float(), nullable=False),
        sa.Column("estimated_people_benefit", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("score_components_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "candidate_id", name="uq_opt_run_candidate"),
    )
    op.create_index("ix_opt_sel_run", "optimization_selections", ["run_id"])

def downgrade():
    op.drop_index("ix_opt_sel_run", table_name="optimization_selections")
    op.drop_table("optimization_selections")
    op.drop_index("ix_opt_runs_area_created", table_name="optimization_runs")
    op.drop_table("optimization_runs")
