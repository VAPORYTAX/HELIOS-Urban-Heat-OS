from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_exposure import DriverAttribution, ExposureMetric, Facility, UrbanContextCell
from app.db.models_thermal import ThermalCell
from app.db.session import get_db
from app.exposure.service import compute_latest_exposure_for_cell

router = APIRouter(tags=["exposure"])

@router.get("/exposure/area")
def area_exposure(area_id: str, db: Session = Depends(get_db)):
    cells = db.execute(
        select(ThermalCell.id).where(ThermalCell.area_id == area_id)
    ).scalars().all()
    metrics = []
    for cell_id in cells:
        row = db.execute(
            select(ExposureMetric)
            .where(ExposureMetric.cell_id == cell_id)
            .order_by(desc(ExposureMetric.observed_at))
            .limit(1)
        ).scalar_one_or_none()
        if row:
            metrics.append(row)
    return {
        "area_id": area_id,
        "cell_count": len(metrics),
        "total_teu": round(sum(x.teu for x in metrics), 6),
        "total_vulnerable_teu": round(sum(x.vulnerable_teu for x in metrics), 6),
        "population_exposed": round(sum(x.population_exposed for x in metrics), 6),
        "vulnerable_population_exposed": round(sum(x.vulnerable_population_exposed for x in metrics), 6),
        "mean_confidence": round(sum(x.confidence for x in metrics) / len(metrics), 6) if metrics else None,
    }

@router.get("/exposure/cells")
def cell_exposure(area_id: str, db: Session = Depends(get_db)):
    cells = db.execute(
        select(ThermalCell.id).where(ThermalCell.area_id == area_id)
    ).scalars().all()
    out = []
    for cell_id in cells:
        metric = db.execute(
            select(ExposureMetric)
            .where(ExposureMetric.cell_id == cell_id)
            .order_by(desc(ExposureMetric.observed_at))
            .limit(1)
        ).scalar_one_or_none()
        context = db.execute(
            select(UrbanContextCell).where(UrbanContextCell.cell_id == cell_id)
        ).scalar_one_or_none()
        if metric and context:
            out.append({
                "cell_id": cell_id,
                "observed_at": metric.observed_at,
                "hazard_index": metric.hazard_index,
                "exposure_index": metric.exposure_index,
                "vulnerability_index": metric.vulnerability_index,
                "teu": metric.teu,
                "vulnerable_teu": metric.vulnerable_teu,
                "population": context.population,
                "vulnerable_population": context.vulnerable_population,
                "confidence": metric.confidence,
            })
    return out

@router.post("/exposure/cells/{cell_id}/compute")
def compute_cell(cell_id: str, db: Session = Depends(get_db)):
    if db.get(ThermalCell, cell_id) is None:
        raise HTTPException(404, detail="thermal cell not found")
    result = compute_latest_exposure_for_cell(db, cell_id)
    if result is None:
        raise HTTPException(409, detail="cell lacks context or thermal metrics")
    metric, driver = result
    return {
        "cell_id": cell_id,
        "teu": metric.teu,
        "vulnerable_teu": metric.vulnerable_teu,
        "dominant_driver": driver.dominant_driver,
        "confidence": metric.confidence,
    }

@router.get("/attribution/area")
def area_attribution(area_id: str, db: Session = Depends(get_db)):
    cells = db.execute(
        select(ThermalCell.id).where(ThermalCell.area_id == area_id)
    ).scalars().all()
    out = []
    for cell_id in cells:
        row = db.execute(
            select(DriverAttribution)
            .where(DriverAttribution.cell_id == cell_id)
            .order_by(desc(DriverAttribution.observed_at))
            .limit(1)
        ).scalar_one_or_none()
        if row:
            out.append({
                "cell_id": row.cell_id,
                "observed_at": row.observed_at,
                "dominant_driver": row.dominant_driver,
                "driver_scores": row.driver_scores_json,
                "confidence": row.confidence,
                "method_version": row.method_version,
                "evidence": row.evidence_json,
            })
    return out

@router.get("/context/cells")
def context_cells(area_id: str, db: Session = Depends(get_db)):
    cells = db.execute(select(ThermalCell.id).where(ThermalCell.area_id == area_id)).scalars().all()
    rows = db.execute(select(UrbanContextCell).where(UrbanContextCell.cell_id.in_(cells))).scalars().all()
    return [{
        "cell_id": r.cell_id,
        "population": r.population,
        "population_density_km2": r.population_density_km2,
        "vulnerable_population": r.vulnerable_population,
        "vulnerability_index": r.vulnerability_index,
        "vegetation_fraction": r.vegetation_fraction,
        "impervious_fraction": r.impervious_fraction,
        "building_fraction": r.building_fraction,
        "shade_fraction": r.shade_fraction,
        "road_fraction": r.road_fraction,
        "solar_exposure_index": r.solar_exposure_index,
        "nighttime_retention_index": r.nighttime_retention_index,
        "data_quality": r.data_quality,
        "source": r.source_json,
    } for r in rows]

@router.get("/facilities")
def facilities(area_id: str, db: Session = Depends(get_db)):
    rows = db.execute(select(Facility).where(Facility.area_id == area_id)).scalars().all()
    return [{
        "id": r.id,
        "name": r.name,
        "facility_type": r.facility_type,
        "vulnerability_weight": r.vulnerability_weight,
        "capacity": r.capacity,
        "metadata": r.metadata_json,
    } for r in rows]
