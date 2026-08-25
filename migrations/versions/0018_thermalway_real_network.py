"""Real OSM ThermalWay routing network."""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
revision="0018_thermalway_real"
down_revision="0017_decision_thermalway"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "thermalway_osm_nodes",
        sa.Column("osm_node_id",sa.BigInteger(),primary_key=True),
        sa.Column("geometry",Geometry("POINT",srid=4326),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_table(
        "thermalway_osm_edges",
        sa.Column("id",sa.String(64),primary_key=True),
        sa.Column("osm_way_id",sa.BigInteger(),nullable=False),
        sa.Column("u",sa.BigInteger(),nullable=False),
        sa.Column("v",sa.BigInteger(),nullable=False),
        sa.Column("geometry",Geometry("LINESTRING",srid=4326),nullable=False),
        sa.Column("length_m",sa.Float(),nullable=False),
        sa.Column("highway",sa.String(64),nullable=True),
        sa.Column("name",sa.String(256),nullable=True),
        sa.Column("foot",sa.String(64),nullable=True),
        sa.Column("sidewalk",sa.String(64),nullable=True),
        sa.Column("covered",sa.String(32),nullable=True),
        sa.Column("access",sa.String(64),nullable=True),
        sa.Column("tags_json",sa.JSON(),nullable=False),
        sa.Column("source",sa.String(64),nullable=False),
        sa.Column("source_timestamp",sa.DateTime(timezone=True),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_table(
        "thermalway_route_runs",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("area_id",sa.String(64),nullable=False),
        sa.Column("mode",sa.String(32),nullable=False),
        sa.Column("traveler_profile",sa.String(64),nullable=False),
        sa.Column("origin_json",sa.JSON(),nullable=False),
        sa.Column("destination_json",sa.JSON(),nullable=False),
        sa.Column("route_json",sa.JSON(),nullable=False),
        sa.Column("distance_m",sa.Float(),nullable=False),
        sa.Column("duration_min",sa.Float(),nullable=False),
        sa.Column("thermal_exposure_cost",sa.Float(),nullable=False),
        sa.Column("confidence",sa.Float(),nullable=False),
        sa.Column("truth_category",sa.String(64),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),
    )
    op.create_index("ix_tw_edges_u","thermalway_osm_edges",["u"])
    op.create_index("ix_tw_edges_v","thermalway_osm_edges",["v"])
    op.create_index("ix_tw_route_area","thermalway_route_runs",["area_id"])

def downgrade():
    op.drop_index("ix_tw_route_area",table_name="thermalway_route_runs")
    op.drop_index("ix_tw_edges_v",table_name="thermalway_osm_edges")
    op.drop_index("ix_tw_edges_u",table_name="thermalway_osm_edges")
    op.drop_table("thermalway_route_runs")
    op.drop_table("thermalway_osm_edges")
    op.drop_table("thermalway_osm_nodes")
