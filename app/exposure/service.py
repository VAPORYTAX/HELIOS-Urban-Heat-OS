from datetime import datetime, timezone

from geoalchemy2.shape import to_shape
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_exposure import DriverAttribution, ExposureMetric, Facility, UrbanContextCell
from app.db.models_thermal import ThermalCell, ThermalMetric, ThermalObservation
from app.exposure.metrics import compute_exposure_index, compute_hazard_index, compute_teu
from app.attribution.engine import attribute_drivers

def _facility_weight_for_cell(db: Session, cell: ThermalCell) -> float:
    # PostGIS-free containment fallback for deterministic fixture sizes:
    # inspect facility points via Shapely against the already-loaded cell geometry.
    cell_shape = to_shape(cell.geometry)
    facilities = db.execute(select(Facility).where(Facility.area_id == cell.area_id)).scalars().all()
    score = 0.0
    for facility in facilities:
        if cell_shape.contains(to_shape(facility.geometry)) or cell_shape.touches(to_shape(facility.geometry)):
            score += max(0.0, facility.vulnerability_weight)
    return score

def compute_latest_exposure_for_cell(db: Session, cell_id: str):
    cell = db.get(ThermalCell, cell_id)
    context = db.execute(
        select(UrbanContextCell).where(UrbanContextCell.cell_id == cell_id)
    ).scalar_one_or_none()
    metric = db.execute(
        select(ThermalMetric)
        .where(ThermalMetric.cell_id == cell_id)
        .order_by(desc(ThermalMetric.observed_at))
        .limit(1)
    ).scalar_one_or_none()
    obs = db.execute(
        select(ThermalObservation)
        .where(ThermalObservation.cell_id == cell_id)
        .order_by(desc(ThermalObservation.observed_at))
        .limit(1)
    ).scalar_one_or_none()

    if not cell or not context or not metric or not obs:
        return None

    facility_weight = _facility_weight_for_cell(db, cell)
    hazard = compute_hazard_index(
        severity_score=metric.severity_score,
        persistence_hours=metric.persistence_hours,
        apparent_temperature_c=obs.apparent_temperature_c,
    )
    exposure_index = compute_exposure_index(
        population_density_km2=context.population_density_km2,
        facility_weight_sum=facility_weight,
    )
    combined_confidence = min(1.0, 0.55 * metric.confidence + 0.45 * context.data_quality)

    result = compute_teu(
        hazard_index=hazard,
        population=context.population,
        vulnerable_population=context.vulnerable_population,
        vulnerability_index=context.vulnerability_index,
        facility_exposure_score=facility_weight * hazard,
        confidence=combined_confidence,
    )

    row = db.execute(
        select(ExposureMetric).where(
            ExposureMetric.cell_id == cell_id,
            ExposureMetric.observed_at == obs.observed_at,
        )
    ).scalar_one_or_none()
    if row is None:
        row = ExposureMetric(cell_id=cell_id, observed_at=obs.observed_at)
        db.add(row)

    row.hazard_index = result.hazard_index
    row.exposure_index = exposure_index
    row.vulnerability_index = result.vulnerability_index
    row.teu = result.teu
    row.vulnerable_teu = result.vulnerable_teu
    row.population_exposed = result.population_exposed
    row.vulnerable_population_exposed = result.vulnerable_population_exposed
    row.facility_exposure_score = result.facility_exposure_score
    row.confidence = result.confidence
    row.components_json = {
        **result.components,
        "population_density_km2": context.population_density_km2,
        "facility_weight_sum": facility_weight,
    }

    attrib = attribute_drivers(
        vegetation_fraction=context.vegetation_fraction,
        impervious_fraction=context.impervious_fraction,
        building_fraction=context.building_fraction,
        shade_fraction=context.shade_fraction,
        road_fraction=context.road_fraction,
        solar_exposure_index=context.solar_exposure_index,
        nighttime_retention_index=context.nighttime_retention_index,
        anomaly_c=metric.anomaly_c,
        persistence_hours=metric.persistence_hours,
        context_quality=context.data_quality,
        thermal_confidence=metric.confidence,
    )

    driver = db.execute(
        select(DriverAttribution).where(
            DriverAttribution.cell_id == cell_id,
            DriverAttribution.observed_at == obs.observed_at,
        )
    ).scalar_one_or_none()
    if driver is None:
        driver = DriverAttribution(cell_id=cell_id, observed_at=obs.observed_at)
        db.add(driver)

    driver.dominant_driver = attrib["dominant_driver"]
    driver.driver_scores_json = attrib["driver_scores"]
    driver.confidence = attrib["confidence"]
    driver.method_version = attrib["method_version"]
    driver.evidence_json = attrib["evidence"]

    db.commit()
    db.refresh(row)
    db.refresh(driver)
    return row, driver
