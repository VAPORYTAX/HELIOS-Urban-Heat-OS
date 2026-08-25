from __future__ import annotations
from sqlalchemy import inspect, text
from app.db.models_decision_science import ThermalWayNetworkAudit

ROAD_HINTS = ("road", "street", "edge", "network", "osm")
GEOM_HINTS = ("geom", "geometry", "the_geom")

def _safe_line_count(db, table, geom):
    try:
        with db.begin_nested():
            sql = (
                'SELECT COUNT(*) FROM "' + table + '" '
                'WHERE UPPER(REPLACE(ST_GeometryType("' + geom + '"), \'ST_\', \'\')) '
                "IN ('LINESTRING','MULTILINESTRING')"
            )
            return int(db.execute(text(sql)).scalar() or 0), None
    except Exception as exc:
        return 0, f"{type(exc).__name__}: {exc}"

def audit_real_network(db, area_id="phx-downtown"):
    ins = inspect(db.get_bind())
    candidates = []
    best = None

    for table in ins.get_table_names():
        if not any(h in table.lower() for h in ROAD_HINTS):
            continue

        try:
            cols = ins.get_columns(table)
        except Exception as exc:
            candidates.append({
                "table": table,
                "geometry_column": None,
                "columns": [],
                "line_feature_count": 0,
                "probe_error": f"column inspection failed: {type(exc).__name__}: {exc}",
            })
            continue

        names = [c["name"] for c in cols]
        geom = next((n for n in names if n.lower() in GEOM_HINTS or "geom" in n.lower()), None)
        if not geom:
            candidates.append({
                "table": table,
                "geometry_column": None,
                "columns": names,
                "line_feature_count": 0,
                "probe_error": "no geometry-like column discovered",
            })
            continue

        count, err = _safe_line_count(db, table, geom)
        candidate = {
            "table": table,
            "geometry_column": geom,
            "columns": names,
            "line_feature_count": count,
            "probe_error": err,
        }
        candidates.append(candidate)

        if count > 0 and (best is None or count > best["line_feature_count"]):
            best = candidate

    proven = bool(best and best["line_feature_count"] >= 10)
    status = "ready_for_real_routing" if proven else "network_schema_required"

    row = ThermalWayNetworkAudit(
        area_id=area_id,
        status=status,
        source_table=best["table"] if best else None,
        geometry_column=best["geometry_column"] if best else None,
        candidate_tables_json=candidates,
        line_feature_count=best["line_feature_count"] if best else 0,
        real_osm_network_proven=proven,
        notes_json={
            "claim_boundary": "ThermalWay real-street routing is enabled only after a real line network is proven.",
            "required_next_if_blocked": "Wire the discovered real OSM/road line table into ThermalWay graph construction.",
            "synthetic_routes_created": False,
            "transaction_isolation": "candidate probes use SQL SAVEPOINTs",
        },
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
