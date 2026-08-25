"""Checkpointed FortyGuard operational history."""
from alembic import op
import sqlalchemy as sa
revision="0014_fg_ckpt"
down_revision="0013_fg_hist"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "fortyguard_history_checkpoints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("request_key", sa.String(160), nullable=False, unique=True),
        sa.Column("area_id", sa.String(64), nullable=False),
        sa.Column("request_kind", sa.String(32), nullable=False),
        sa.Column("request_date", sa.Date(), nullable=True),
        sa.Column("activity_id", sa.String(64), nullable=True),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_fg_hist_ckpt_area_kind","fortyguard_history_checkpoints",["area_id","request_kind"])

def downgrade():
    op.drop_index("ix_fg_hist_ckpt_area_kind",table_name="fortyguard_history_checkpoints")
    op.drop_table("fortyguard_history_checkpoints")
