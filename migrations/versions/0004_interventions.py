"""Intervention intelligence and counterfactual scenarios."""
from alembic import op
import sqlalchemy as sa

revision = "0004_interventions"
down_revision = "0003_exposure_core"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "intervention_catalog",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("effect_profile_json", sa.JSON(), nullable=False),
        sa.Column("cost_model_json", sa.JSON(), nullable=False),
        sa.Column("constraints_json", sa.JSON(), nullable=False),
        sa.Column("evidence_level", sa.String(32), nullable=False),
        sa.Column("base_confidence", sa.Float(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "intervention_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("cell_id", sa.String(64), sa.ForeignKey("thermal_cells.id", ondelete="CASCADE"), nullable=False),
        sa.Column("intervention_id", sa.String(64), sa.ForeignKey("intervention_catalog.id", ondelete="CASCADE"), nullable=False),
        sa.Column("suitability_score", sa.Float(), nullable=False),
        sa.Column("estimated_cost", sa.Float(), nullable=False),
        sa.Column("implementation_months", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reasons_json", sa.JSON(), nullable=False),
        sa.Column("constraints_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("cell_id", "intervention_id", name="uq_candidate_cell_intervention"),
    )
    op.create_index("ix_candidates_cell", "intervention_candidates", ["cell_id"])

    op.create_table(
        "scenarios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("area_id", sa.String(64), sa.ForeignKey("areas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("objective", sa.String(64), nullable=False),
        sa.Column("budget", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "scenario_interventions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scenario_id", sa.String(36), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_id", sa.String(36), sa.ForeignKey("intervention_candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False, server_default="1"),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("scenario_id", "candidate_id", name="uq_scenario_candidate"),
    )

    op.create_table(
        "scenario_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scenario_id", sa.String(36), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("baseline_teu", sa.Float(), nullable=False),
        sa.Column("projected_teu", sa.Float(), nullable=False),
        sa.Column("teu_reduction", sa.Float(), nullable=False),
        sa.Column("teu_reduction_pct", sa.Float(), nullable=False),
        sa.Column("baseline_vulnerable_teu", sa.Float(), nullable=False),
        sa.Column("projected_vulnerable_teu", sa.Float(), nullable=False),
        sa.Column("vulnerable_teu_reduction", sa.Float(), nullable=False),
        sa.Column("total_cost", sa.Float(), nullable=False),
        sa.Column("thermal_roi", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("lower_teu_reduction", sa.Float(), nullable=False),
        sa.Column("upper_teu_reduction", sa.Float(), nullable=False),
        sa.Column("assumptions_json", sa.JSON(), nullable=False),
        sa.Column("cell_results_json", sa.JSON(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table("scenario_results")
    op.drop_table("scenario_interventions")
    op.drop_table("scenarios")
    op.drop_index("ix_candidates_cell", table_name="intervention_candidates")
    op.drop_table("intervention_candidates")
    op.drop_table("intervention_catalog")
