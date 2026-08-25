from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_realdata import DataSyncRun
from app.db.session import get_db
from app.realdata.readiness import provider_readiness
from app.realdata.service import sync_osm

router = APIRouter(prefix="/data", tags=["real-data"])

@router.get("/readiness")
def readiness():
    return provider_readiness()

@router.post("/sync/osm")
def osm_sync(area_id: str, db: Session = Depends(get_db)):
    try:
        r = sync_osm(db, area_id)
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, detail=f"OSM sync failed: {exc}") from exc
    return {
        "run_id": r.id, "provider": r.provider, "status": r.status,
        "truth_category": r.truth_category,
        "records_received": r.records_received,
        "records_applied": r.records_applied,
        "details": r.details_json,
    }

@router.get("/sync/runs")
def sync_runs(area_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        select(DataSyncRun).where(DataSyncRun.area_id == area_id)
        .order_by(desc(DataSyncRun.started_at))
    ).scalars().all()
    return [{
        "id": r.id, "provider": r.provider, "status": r.status,
        "truth_category": r.truth_category, "started_at": r.started_at,
        "completed_at": r.completed_at, "records_received": r.records_received,
        "records_applied": r.records_applied, "details": r.details_json,
        "error": r.error_text,
    } for r in rows]
