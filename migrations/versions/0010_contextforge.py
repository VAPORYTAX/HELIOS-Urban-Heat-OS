"""ContextForge decision packets and prompt registry."""
from alembic import op
import sqlalchemy as sa
revision = "0010_contextforge"
down_revision = "0009_hardening"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table(
        "prompt_registry",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("role", sa.String(64), nullable=False),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("name","version",name="uq_prompt_name_version"),
    )
    op.create_table(
        "context_packets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("area_id", sa.String(64), nullable=False),
        sa.Column("task_type", sa.String(64), nullable=False),
        sa.Column("mode", sa.String(32), nullable=False),
        sa.Column("user_intent", sa.Text(), nullable=False),
        sa.Column("context_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("prompt_bundle_version", sa.String(64), nullable=False),
        sa.Column("token_budget", sa.Integer(), nullable=False),
        sa.Column("estimated_tokens", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("packet_json", sa.JSON(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_context_area_created","context_packets",["area_id","created_at"])
def downgrade():
    op.drop_index("ix_context_area_created",table_name="context_packets")
    op.drop_table("context_packets")
    op.drop_table("prompt_registry")
