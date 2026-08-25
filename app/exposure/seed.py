from datetime import datetime, timezone

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import delete, select

from app.db.models_exposure import DriverAttribution, ExposureMetric, Facility, UrbanContextCell
from app.db.models_thermal import ThermalCell
from app.db.session import SessionLocal
from app.exposure.fixture import CONTEXT_FIXTURE, FACILITY_FIXTURE
from app.exposure.service import compute_latest_exposure_for_cell

def seed_exposure(reset: bool = False):
    db = SessionLocal()
    try:
        if reset:
            db.execute(delete(DriverAttribution))
            db.execute(delete(ExposureMetric))
            db.execute(delete(Facility).where(Facility.area_id == "phx-downtown"))
            db.execute(delete(UrbanContextCell))
            db.commit()

        for cell_id, values in CONTEXT_FIXTURE.items():
            row = db.execute(
                select(UrbanContextCell).where(UrbanContextCell.cell_id == cell_id)
            ).scalar_one_or_none()
            if row is None:
                row = UrbanContextCell(cell_id=cell_id)
                db.add(row)
            for key, value in values.items():
                setattr(row, key, value)
            row.source_json = {
                "mode": "fixture",
                "source": "helios-context-fixture-v1",
                "truth_category": "fixture",
            }
            row.updated_at = datetime.now(timezone.utc)

        for item in FACILITY_FIXTURE:
            row = db.get(Facility, item["id"])
            if row is None:
                row = Facility(id=item["id"])
                db.add(row)
            row.area_id = item["area_id"]
            row.name = item["name"]
            row.facility_type = item["facility_type"]
            row.vulnerability_weight = item["vulnerability_weight"]
            row.capacity = item["capacity"]
            row.geometry = from_shape(Point(item["longitude"], item["latitude"]), srid=4326)
            row.metadata_json = {"mode": "fixture", "truth_category": "fixture"}

        db.commit()

        cell_ids = db.execute(
            select(ThermalCell.id).where(ThermalCell.area_id == "phx-downtown")
        ).scalars().all()

        results = []
        for cell_id in cell_ids:
            computed = compute_latest_exposure_for_cell(db, cell_id)
            if computed:
                metric, driver = computed
                results.append({
                    "cell_id": cell_id,
                    "teu": metric.teu,
                    "vulnerable_teu": metric.vulnerable_teu,
                    "dominant_driver": driver.dominant_driver,
                    "confidence": metric.confidence,
                })

        return {
            "area": "phx-downtown",
            "context_cells": len(CONTEXT_FIXTURE),
            "facilities": len(FACILITY_FIXTURE),
            "computed_cells": len(results),
            "results": results,
        }
    finally:
        db.close()
