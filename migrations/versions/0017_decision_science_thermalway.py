"""Advanced decision science and ThermalWay routing evidence."""
from alembic import op
import sqlalchemy as sa
revision="0017_decision_thermalway"
down_revision="0016_provider_decision"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "decision_science_runs",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("optimizer_run_id",sa.String(36),nullable=False),
        sa.Column("status",sa.String(32),nullable=False),
        sa.Column("robustness_score",sa.Float(),nullable=False),
        sa.Column("max_regret",sa.Float(),nullable=False),
        sa.Column("mean_regret",sa.Float(),nullable=False),
        sa.Column("sensitivity_json",sa.JSON(),nullable=False),
        sa.Column("voi_json",sa.JSON(),nullable=False),
        sa.Column("reverse_optimization_json",sa.JSON(),nullable=False),
        sa.Column("sequencing_json",sa.JSON(),nullable=False),
        sa.Column("what_changes_mind_json",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_table(
        "thermalway_network_audits",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("status",sa.String(32),nullable=False),
        sa.Column("source_table",sa.String(128),nullable=True),
        sa.Column("geometry_column",sa.String(128),nullable=True),
        sa.Column("candidate_tables_json",sa.JSON(),nullable=False),
        sa.Column("line_feature_count",sa.Integer(),nullable=False),
        sa.Column("real_osm_network_proven",sa.Boolean(),nullable=False),
        sa.Column("notes_json",sa.JSON(),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_decision_science_area","decision_science_runs",["area_id"])
    op.create_index("ix_thermalway_audit_area","thermalway_network_audits",["area_id"])

def downgrade():
    op.drop_index("ix_thermalway_audit_area",table_name="thermalway_network_audits")
    op.drop_index("ix_decision_science_area",table_name="decision_science_runs")
    op.drop_table("thermalway_network_audits")
    op.drop_table("decision_science_runs")
