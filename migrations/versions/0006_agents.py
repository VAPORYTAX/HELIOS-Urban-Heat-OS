"""Agentic decision, evidence, review and recommendation layer."""
from alembic import op
import sqlalchemy as sa

revision = "0006_agents"
down_revision = "0005_optimizer"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("area_id", sa.String(64), sa.ForeignKey("areas.id", ondelete="CASCADE"), nullable=False),
        sa.Column("optimization_run_id", sa.String(36), sa.ForeignKey("optimization_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("request_json", sa.JSON(), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("requires_human_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_agent_runs_area_created", "agent_runs", ["area_id", "created_at"])

    op.create_table(
        "agent_findings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(64), nullable=False),
        sa.Column("finding_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_agent_findings_run_agent", "agent_findings", ["run_id", "agent_name"])

    op.create_table(
        "evidence_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim_key", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_ref", sa.String(256), nullable=False),
        sa.Column("truth_category", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evidence_run_claim", "evidence_records", ["run_id", "claim_key"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("headline", sa.String(256), nullable=False),
        sa.Column("decision_status", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("requires_human_review", sa.Boolean(), nullable=False),
        sa.Column("recommended_actions_json", sa.JSON(), nullable=False),
        sa.Column("skeptic_findings_json", sa.JSON(), nullable=False),
        sa.Column("evidence_summary_json", sa.JSON(), nullable=False),
        sa.Column("executive_summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade():
    op.drop_table("recommendations")
    op.drop_index("ix_evidence_run_claim", table_name="evidence_records")
    op.drop_table("evidence_records")
    op.drop_index("ix_agent_findings_run_agent", table_name="agent_findings")
    op.drop_table("agent_findings")
    op.drop_index("ix_agent_runs_area_created", table_name="agent_runs")
    op.drop_table("agent_runs")
