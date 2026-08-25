from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models_demographics import CellDemographic
from app.db.session import get_db
from app.realdata.census import status as census_status
from app.realdata.demographics import sync_census_demographics

router = APIRouter(prefix="/demographics", tags=["demographics"])

@router.get("/readiness")
def readiness():
    return census_status()

@router.post("/sync")
def sync(area_id: str, db: Session = Depends(get_db)):
    try:
        run = sync_census_demographics(db, area_id)
    except Exception as exc:
        raise HTTPException(502, detail=f"Census sync failed: {exc}") from exc
    return {
        "run_id": run.id,
        "provider": run.provider,
        "status": run.status,
        "records_received": run.records_received,
        "records_applied": run.records_applied,
        "details": run.details_json,
    }

@router.get("/cells")
def cells(area_id: str, db: Session = Depends(get_db)):
    from app.db.models_thermal import ThermalCell
    cell_ids = db.execute(
        select(ThermalCell.id).where(ThermalCell.area_id == area_id)
    ).scalars().all()
    rows = db.execute(
        select(CellDemographic).where(CellDemographic.cell_id.in_(cell_ids))
    ).scalars().all()
    return [{
        "cell_id": r.cell_id,
        "population": r.population,
        "population_density_km2": r.population_density_km2,
        "under5_population": r.under5_population,
        "age65_population": r.age65_population,
        "poverty_population": r.poverty_population,
        "no_vehicle_households": r.no_vehicle_households,
        "vulnerability_index": r.vulnerability_index,
        "derived_vulnerable_population": r.derived_vulnerable_population,
        "confidence": r.confidence,
        "allocation": r.allocation_json,
        "source": r.source_json,
    } for r in rows]
