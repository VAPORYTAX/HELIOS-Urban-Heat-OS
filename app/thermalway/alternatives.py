from __future__ import annotations
from collections import defaultdict
import inspect
from sqlalchemy import desc, select
from geoalchemy2.shape import to_shape

from app.db.models_thermalway import ThermalWayOSMNode, ThermalWayOSMEdge
from app.db.models_provider_ops import ProviderOperationalMetric
from app.db.models_thermal import ThermalCell
from app.thermalway.router import _nearest, _edge_cell, _cost, WALK_MPS
from app.thermalway.algorithms import yen_k_routes


def _call_yen_compat(adj, start, goal, coords, k):
    """
    Compatibility shim for both HELIOS Yen implementations:
      newer: yen_k_routes(adj,start,goal,coords,k=...,base_algorithm="astar")
      older: yen_k_routes(adj,start,goal,coords,k=...)
    """
    params = inspect.signature(yen_k_routes).parameters
    kwargs = {"k": max(1, min(int(k), 5))}
    if "base_algorithm" in params:
        kwargs["base_algorithm"] = "astar"
    return yen_k_routes(adj, start, goal, coords, **kwargs)


def k_thermal_alternatives(
    db,
    origin_lon,
    origin_lat,
    dest_lon,
    dest_lat,
    profile="standard",
    area_id="phx-downtown",
    k=3,
):
    nodes_raw = db.execute(select(ThermalWayOSMNode)).scalars().all()
    edges = db.execute(select(ThermalWayOSMEdge)).scalars().all()
    if not nodes_raw or not edges:
        raise RuntimeError("ThermalWay OSM network not loaded")

    nodes = [
        (n.osm_node_id, to_shape(n.geometry).x, to_shape(n.geometry).y)
        for n in nodes_raw
    ]
    coords = {nid: (lon, lat) for nid, lon, lat in nodes}
    start = _nearest(nodes, origin_lon, origin_lat)
    goal = _nearest(nodes, dest_lon, dest_lat)

    cell_rows = db.execute(
        select(ThermalCell).where(ThermalCell.area_id == area_id)
    ).scalars().all()
    cells = [(c.id, to_shape(c.geometry)) for c in cell_rows]

    ops = db.execute(
        select(ProviderOperationalMetric)
        .where(ProviderOperationalMetric.area_id == area_id)
        .order_by(desc(ProviderOperationalMetric.created_at))
    ).scalars().all()
    metrics = {}
    for m in ops:
        metrics.setdefault(m.cell_id, m)

    adj = defaultdict(list)
    for edge in edges:
        geom = to_shape(edge.geometry)
        cell_id = _edge_cell(geom, cells)
        metric = metrics.get(cell_id)
        cost, tec = _cost(edge, metric, profile, "thermal_safe")
        adj[edge.u].append((edge.v, cost, edge, tec))
        adj[edge.v].append((edge.u, cost, edge, tec))

    paths = _call_yen_compat(adj, start, goal, coords, k)

    results = []
    for rank, path in enumerate(paths, 1):
        distance_m = sum(step[2].length_m for step in path)
        tec = sum(step[3] for step in path)
        duration_min = (distance_m / WALK_MPS) / 60.0
        results.append({
            "rank": rank,
            "distance_m": distance_m,
            "duration_min": duration_min,
            "thermal_exposure_cost": tec,
            "edge_count": len(path),
            "edge_ids": [step[2].id for step in path],
            "algorithm": "yen_k_shortest_compatible",
        })

    results.sort(key=lambda r: (r["thermal_exposure_cost"], r["duration_min"]))
    for thermal_rank, row in enumerate(results, 1):
        row["thermal_rank"] = thermal_rank
    return results
