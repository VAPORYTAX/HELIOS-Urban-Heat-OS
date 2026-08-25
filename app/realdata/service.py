from datetime import datetime, timezone
from geoalchemy2.shape import from_shape, to_shape
from shapely.ops import transform
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.models_exposure import Facility, UrbanContextCell
from app.db.models_realdata import DataSyncRun
from app.db.models_thermal import Area, ThermalCell
from app.realdata.osm import TO_UTM, classify_facility, fetch_bbox, road_width_m

def clamp(v):
    return max(0.0, min(1.0, float(v)))

def sync_osm(db: Session, area_id: str):
    area = db.get(Area, area_id)
    if area is None:
        raise ValueError("area not found")

    run = DataSyncRun(
        area_id=area_id,
        provider="openstreetmap_overpass",
        status="running",
        truth_category="observed",
        details_json={"endpoint": "https://overpass-api.de/api/interpreter"},
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        area_shape = to_shape(area.geometry)
        west, south, east, north = area_shape.bounds
        features = fetch_bbox(south, west, north, east)
        run.records_received = len(features)

        cells = db.execute(select(ThermalCell).where(ThermalCell.area_id == area_id)).scalars().all()
        db.execute(delete(Facility).where(Facility.area_id == area_id))
        seen_facilities = set()

        for cell in cells:
            cell_geom = to_shape(cell.geometry)
            cell_m = transform(TO_UTM, cell_geom)
            cell_area = max(cell_m.area, 1.0)
            building_area = 0.0
            veg_area = 0.0
            road_area = 0.0
            source_ids = set()

            for f in features:
                if not f.geometry.intersects(cell_geom):
                    continue
                clipped = f.geometry.intersection(cell_geom)
                if clipped.is_empty:
                    continue
                source_ids.add(f"{f.osm_type}/{f.osm_id}")
                clipped_m = transform(TO_UTM, clipped)
                tags = f.tags

                if "building" in tags and clipped_m.geom_type in {"Polygon", "MultiPolygon"}:
                    building_area += clipped_m.area

                if (
                    tags.get("landuse") in {"grass", "forest", "meadow", "recreation_ground"}
                    or tags.get("leisure") in {"park", "garden"}
                    or tags.get("natural") in {"wood", "scrub"}
                ) and clipped_m.geom_type in {"Polygon", "MultiPolygon"}:
                    veg_area += clipped_m.area

                if "highway" in tags:
                    if clipped_m.geom_type in {"LineString", "MultiLineString"}:
                        road_area += clipped_m.length * road_width_m(tags)
                    elif clipped_m.geom_type in {"Polygon", "MultiPolygon"}:
                        road_area += clipped_m.area

                fac = classify_facility(tags)
                if fac:
                    facility_type, weight = fac
                    key = f"{f.osm_type}-{f.osm_id}"
                    centroid = f.geometry.centroid
                    if key not in seen_facilities and (area_shape.contains(centroid) or area_shape.touches(centroid)):
                        seen_facilities.add(key)
                        db.add(Facility(
                            id=f"osm-{key}",
                            area_id=area_id,
                            name=tags.get("name") or f"OSM {facility_type} {f.osm_id}",
                            facility_type=facility_type,
                            vulnerability_weight=weight,
                            capacity=None,
                            geometry=from_shape(centroid, srid=4326),
                            metadata_json={
                                "truth_category": "observed",
                                "provider": "OpenStreetMap",
                                "osm_type": f.osm_type,
                                "osm_id": f.osm_id,
                                "tags": tags,
                            },
                        ))

            ctx = db.execute(
                select(UrbanContextCell).where(UrbanContextCell.cell_id == cell.id)
            ).scalar_one_or_none()
            if ctx is None:
                ctx = UrbanContextCell(
                    cell_id=cell.id, population=0, population_density_km2=0,
                    vulnerable_population=0, vulnerability_index=0,
                    data_quality=0,
                )
                db.add(ctx)

            previous = dict(ctx.source_json or {})
            building_fraction = clamp(building_area / cell_area)
            road_fraction = clamp(road_area / cell_area)
            vegetation_fraction = clamp(veg_area / cell_area)
            impervious_fraction = clamp(building_fraction + road_fraction)
            shade_proxy = clamp(vegetation_fraction * 0.65)

            ctx.building_fraction = building_fraction
            ctx.road_fraction = road_fraction
            ctx.vegetation_fraction = vegetation_fraction
            ctx.impervious_fraction = impervious_fraction
            ctx.shade_fraction = shade_proxy
            ctx.solar_exposure_index = clamp(1.0 - shade_proxy)
            ctx.data_quality = max(ctx.data_quality, 0.84)
            ctx.source_json = {
                "truth_category": "mixed",
                "layers": {
                    "urban_form": {
                        "truth_category": "observed",
                        "provider": "OpenStreetMap/Overpass",
                        "feature_count": len(source_ids),
                    },
                    "shade_fraction": {
                        "truth_category": "derived",
                        "method": "vegetation_fraction * 0.65 proxy",
                    },
                    "demographics": {
                        "truth_category": previous.get("truth_category", "fixture"),
                        "provider": previous.get("source", "existing"),
                    },
                },
            }
            ctx.updated_at = datetime.now(timezone.utc)

        db.commit()
        run.records_applied = len(cells)
        run.status = "complete"
        run.completed_at = datetime.now(timezone.utc)
        run.details_json = {
            **run.details_json,
            "facilities_applied": len(seen_facilities),
            "urban_context_cells_updated": len(cells),
            "note": "Urban form/facilities real OSM; demographics unchanged.",
        }
        db.commit()
        db.refresh(run)
        return run

    except Exception as exc:
        db.rollback()
        row = db.get(DataSyncRun, run.id)
        if row:
            row.status = "failed"
            row.error_text = str(exc)
            row.completed_at = datetime.now(timezone.utc)
            db.commit()
        raise
