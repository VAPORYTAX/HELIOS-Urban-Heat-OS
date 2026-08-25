from __future__ import annotations
from datetime import datetime, timezone
from math import sqrt

from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import transform
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models_demographics import CensusTractDemographic, CellDemographic
from app.db.models_exposure import UrbanContextCell
from app.db.models_realdata import DataSyncRun
from app.db.models_thermal import ThermalCell
from app.realdata.census import fetch_acs_tracts, fetch_tiger_tract_geometries
from app.realdata.osm import TO_UTM

def clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def vulnerability_index(population, under5, age65, poverty_universe, poverty_population, households, no_vehicle):
    if population <= 0:
        return 0.0, {}
    under5_share = under5 / population
    age65_share = age65 / population
    poverty_share = poverty_population / poverty_universe if poverty_universe > 0 else 0.0
    no_vehicle_share = no_vehicle / households if households > 0 else 0.0

    components = {
        "under5": clamp01(under5_share / 0.10),
        "age65": clamp01(age65_share / 0.25),
        "poverty": clamp01(poverty_share / 0.30),
        "no_vehicle": clamp01(no_vehicle_share / 0.25),
    }
    score = (
        0.20 * components["under5"]
        + 0.30 * components["age65"]
        + 0.30 * components["poverty"]
        + 0.20 * components["no_vehicle"]
    )
    return clamp01(score), {
        "raw_shares": {
            "under5": under5_share,
            "age65": age65_share,
            "poverty": poverty_share,
            "no_vehicle_households": no_vehicle_share,
        },
        "normalized_components": components,
        "weights": {"under5": 0.20, "age65": 0.30, "poverty": 0.30, "no_vehicle": 0.20},
    }

def confidence_from_population_moe(population: float, population_moe: float | None) -> float:
    if population <= 0:
        return 0.50
    ratio = abs(population_moe or 0.0) / population
    return clamp01(0.96 - min(0.40, ratio))

def _as_multi(geom):
    if isinstance(geom, MultiPolygon):
        return geom
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    fixed = geom.buffer(0)
    if isinstance(fixed, Polygon):
        return MultiPolygon([fixed])
    if isinstance(fixed, MultiPolygon):
        return fixed
    raise ValueError("tract geometry is not polygonal")

def sync_census_demographics(db: Session, area_id: str):
    run = DataSyncRun(
        area_id=area_id,
        provider="us_census_acs5_2024",
        status="running",
        truth_category="observed",
        details_json={
            "dataset": "2024 ACS 5-Year Detailed Tables",
            "geography": "tract",
            "allocation": "areal_weighting_v1",
        },
    )
    db.add(run); db.commit(); db.refresh(run)

    try:
        rows = fetch_acs_tracts()
        geometries = fetch_tiger_tract_geometries()
        run.records_received = len(rows)

        by_geoid = {}
        now = datetime.now(timezone.utc)
        for item in rows:
            geom = geometries.get(item["geoid"])
            if geom is None:
                continue
            geom = _as_multi(geom)
            tract = db.get(CensusTractDemographic, item["geoid"])
            if tract is None:
                tract = CensusTractDemographic(geoid=item["geoid"])
                db.add(tract)
            tract.name = item["name"]
            tract.state_fips = item["state"]
            tract.county_fips = item["county"]
            tract.tract_code = item["tract"]
            tract.geometry = from_shape(geom, srid=4326)
            tract.population = item["population"]
            tract.population_moe = item["population_moe"]
            tract.under5_population = item["under5_population"]
            tract.age65_population = item["age65_population"]
            tract.poverty_universe = item["poverty_universe"]
            tract.poverty_population = item["poverty_population"]
            tract.households = item["households"]
            tract.no_vehicle_households = item["no_vehicle_households"]
            tract.source_year = 2024
            tract.source_dataset = "acs/acs5"
            tract.variables_json = {
                "population": "B01001_001E",
                "under5": ["B01001_003E", "B01001_027E"],
                "age65_plus": [
                    *[f"B01001_{i:03d}E" for i in range(20, 26)],
                    *[f"B01001_{i:03d}E" for i in range(44, 50)],
                ],
                "poverty_universe": "B17001_001E",
                "poverty_population": "B17001_002E",
                "households": "B08201_001E",
                "no_vehicle_households": "B08201_002E",
            }
            tract.quality_json = {
                "population_moe": item["population_moe"],
                "under5_moe_rss": item["under5_moe"],
                "age65_moe_rss": item["age65_moe"],
                "poverty_population_moe": item["poverty_population_moe"],
                "no_vehicle_households_moe": item["no_vehicle_households_moe"],
                "note": "ACS estimates carry sampling uncertainty; RSS used for grouped MOE approximation.",
            }
            tract.updated_at = now
            by_geoid[item["geoid"]] = (item, geom)

        db.commit()

        cells = db.execute(select(ThermalCell).where(ThermalCell.area_id == area_id)).scalars().all()
        applied = 0

        for cell in cells:
            cell_geom = to_shape(cell.geometry)
            cell_m = transform(TO_UTM, cell_geom)
            cell_area_m2 = max(cell_m.area, 1.0)

            population = under5 = age65 = poverty_population = no_vehicle = 0.0
            poverty_universe = households = 0.0
            conf_weight = 0.0
            conf_sum = 0.0
            allocations = []

            for geoid, (item, tract_geom) in by_geoid.items():
                if not tract_geom.intersects(cell_geom):
                    continue
                tract_m = transform(TO_UTM, tract_geom)
                intersection = tract_geom.intersection(cell_geom)
                if intersection.is_empty or tract_m.area <= 0:
                    continue
                overlap_m = transform(TO_UTM, intersection)
                share = clamp01(overlap_m.area / tract_m.area)
                if share <= 0:
                    continue

                population += item["population"] * share
                under5 += item["under5_population"] * share
                age65 += item["age65_population"] * share
                poverty_universe += item["poverty_universe"] * share
                poverty_population += item["poverty_population"] * share
                households += item["households"] * share
                no_vehicle += item["no_vehicle_households"] * share

                tract_conf = confidence_from_population_moe(item["population"], item["population_moe"])
                weight = max(item["population"] * share, 1.0)
                conf_sum += tract_conf * weight
                conf_weight += weight
                allocations.append({"geoid": geoid, "tract_area_share": share})

            vuln, components = vulnerability_index(
                population, under5, age65, poverty_universe,
                poverty_population, households, no_vehicle,
            )
            confidence = conf_sum / conf_weight if conf_weight else 0.50
            vulnerable_population = population * vuln
            density = population / (cell_area_m2 / 1_000_000.0)

            cell_demo = db.execute(
                select(CellDemographic).where(CellDemographic.cell_id == cell.id)
            ).scalar_one_or_none()
            if cell_demo is None:
                cell_demo = CellDemographic(cell_id=cell.id)
                db.add(cell_demo)

            cell_demo.population = population
            cell_demo.population_density_km2 = density
            cell_demo.under5_population = under5
            cell_demo.age65_population = age65
            cell_demo.poverty_population = poverty_population
            cell_demo.no_vehicle_households = no_vehicle
            cell_demo.vulnerability_index = vuln
            cell_demo.derived_vulnerable_population = vulnerable_population
            cell_demo.confidence = confidence
            cell_demo.allocation_json = {"method": "areal_weighting_v1", "tracts": allocations}
            cell_demo.source_json = {
                "truth_category": "derived",
                "population_source": "US Census ACS 2024 observed tract estimates",
                "geometry_source": "Census TIGERweb ACS 2024",
                "vulnerability_method": "helios_demographic_vulnerability_v1",
            }
            cell_demo.updated_at = now

            ctx = db.execute(
                select(UrbanContextCell).where(UrbanContextCell.cell_id == cell.id)
            ).scalar_one_or_none()
            if ctx is None:
                continue

            existing_layers = dict((ctx.source_json or {}).get("layers") or {})
            ctx.population = population
            ctx.population_density_km2 = density
            ctx.vulnerable_population = vulnerable_population
            ctx.vulnerability_index = vuln
            ctx.data_quality = min(1.0, 0.55 * ctx.data_quality + 0.45 * confidence)
            existing_layers["demographics"] = {
                "truth_category": "derived",
                "provider": "US Census ACS 2024 + TIGERweb",
                "source_geography": "tract",
                "allocation": "areal_weighting_v1",
                "population_truth": "observed ACS estimate",
                "cell_population_truth": "derived allocation",
                "vulnerability_truth": "derived index",
                "confidence": confidence,
                "components": components,
            }
            ctx.source_json = {"truth_category": "mixed", "layers": existing_layers}
            ctx.updated_at = now
            applied += 1

        db.commit()
        run.records_applied = applied
        run.status = "complete"
        run.completed_at = now
        run.details_json = {
            **run.details_json,
            "acs_tracts_received": len(rows),
            "tract_geometries_received": len(geometries),
            "cells_updated": applied,
            "population_cell_truth": "derived_from_observed_acs",
            "vulnerability_truth": "derived",
        }
        db.commit(); db.refresh(run)
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
