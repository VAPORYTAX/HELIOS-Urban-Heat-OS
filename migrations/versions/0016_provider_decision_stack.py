"""Provider-native counterfactual, optimizer, and governed decision stack."""
from alembic import op
import sqlalchemy as sa
revision="0016_provider_decision"
down_revision="0015_provider_ops"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "provider_intervention_candidates",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("run_id",sa.String(36),nullable=False),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("cell_id",sa.String(64),nullable=False),
        sa.Column("intervention_type",sa.String(64),nullable=False),
        sa.Column("cost",sa.Float(),nullable=False),
        sa.Column("temperature_delta_c",sa.Float(),nullable=False),
        sa.Column("teu_reduction",sa.Float(),nullable=False),
        sa.Column("va_teu_reduction",sa.Float(),nullable=False),
        sa.Column("people_benefit_proxy",sa.Float(),nullable=False),
        sa.Column("feasibility",sa.Float(),nullable=False),
        sa.Column("confidence",sa.Float(),nullable=False),
        sa.Column("assumption_json",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_table(
        "provider_optimizer_runs",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("budget",sa.Float(),nullable=False),
        sa.Column("objective",sa.String(64),nullable=False),
        sa.Column("status",sa.String(32),nullable=False),
        sa.Column("selected_json",sa.JSON(),nullable=False),
        sa.Column("total_cost",sa.Float(),nullable=False),
        sa.Column("teu_reduction",sa.Float(),nullable=False),
        sa.Column("va_teu_reduction",sa.Float(),nullable=False),
        sa.Column("confidence",sa.Float(),nullable=False),
        sa.Column("source_metric_ids",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_table(
        "provider_agent_decisions",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("optimizer_run_id",sa.String(36),nullable=False),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("status",sa.String(32),nullable=False),
        sa.Column("confidence",sa.Float(),nullable=False),
        sa.Column("requires_human_review",sa.Boolean(),nullable=False),
        sa.Column("agent_actions_json",sa.JSON(),nullable=False),
        sa.Column("evidence_json",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_provider_candidate_run","provider_intervention_candidates",["run_id"])
    op.create_index("ix_provider_optimizer_area","provider_optimizer_runs",["area_id"])
    op.create_index("ix_provider_agent_area","provider_agent_decisions",["area_id"])

def downgrade():
    op.drop_index("ix_provider_agent_area",table_name="provider_agent_decisions")
    op.drop_index("ix_provider_optimizer_area",table_name="provider_optimizer_runs")
    op.drop_index("ix_provider_candidate_run",table_name="provider_intervention_candidates")
    op.drop_table("provider_agent_decisions")
    op.drop_table("provider_optimizer_runs")
    op.drop_table("provider_intervention_candidates")
