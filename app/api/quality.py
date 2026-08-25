from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_quality import QualitySnapshot, SystemAuditEvent
from app.db.session import get_db
from app.quality.service import run_quality_snapshot

router = APIRouter(prefix="/quality", tags=["quality"])

@router.post("/snapshot")
def snapshot(area_id: str, fortyguard_live: bool = False, db: Session = Depends(get_db)):
    r = run_quality_snapshot(db, area_id, fortyguard_live=fortyguard_live)
    return {
        "id": r.id,
        "area_id": r.area_id,
        "status": r.status,
        "health_score": r.health_score,
        "requires_human_review": r.requires_human_review,
        "checks": r.checks_json,
        "created_at": r.created_at,
    }

@router.get("/latest")
def latest(area_id: str, db: Session = Depends(get_db)):
    r = db.execute(
        select(QualitySnapshot)
        .where(QualitySnapshot.area_id == area_id)
        .order_by(desc(QualitySnapshot.created_at))
        .limit(1)
    ).scalar_one_or_none()
    if r is None:
        return None
    return {
        "id": r.id, "area_id": r.area_id, "status": r.status,
        "health_score": r.health_score,
        "requires_human_review": r.requires_human_review,
        "checks": r.checks_json, "created_at": r.created_at,
    }

@router.get("/audit")
def audit(area_id: str, limit: int = 50, db: Session = Depends(get_db)):
    rows = db.execute(
        select(SystemAuditEvent)
        .where(SystemAuditEvent.area_id == area_id)
        .order_by(desc(SystemAuditEvent.created_at))
        .limit(max(1, min(limit, 200)))
    ).scalars().all()
    return [{
        "id": r.id, "event_type": r.event_type, "severity": r.severity,
        "message": r.message, "entity_type": r.entity_type,
        "entity_id": r.entity_id, "details": r.details_json,
        "created_at": r.created_at,
    } for r in rows]
