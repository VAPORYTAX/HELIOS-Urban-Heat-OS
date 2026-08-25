from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from app.db.models_intelligence import IntelligenceRun
from app.db.session import get_db
from app.intelligence.contracts import IntelligenceQuery
from app.intelligence.gateway import readiness
from app.intelligence.service import run_intelligence

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

@router.get("/readiness")
def ready():
    return readiness()

@router.post("/query")
def query(body: IntelligenceQuery, db: Session = Depends(get_db)):
    try:
        run = run_intelligence(db, body)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    return {
        "run_id": run.id,
        "context_packet_id": run.context_packet_id,
        "provider": run.provider,
        "model": run.model_name,
        "thinking_enabled": run.thinking_enabled,
        "status": run.status,
        "fallback_used": run.fallback_used,
        "latency_ms": run.latency_ms,
        "answer": run.response_json,
        "validation": run.validation_json,
    }

@router.get("/runs")
def runs(area_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        select(IntelligenceRun).where(IntelligenceRun.area_id == area_id)
        .order_by(desc(IntelligenceRun.created_at))
    ).scalars().all()
    return [{
        "id": r.id, "context_packet_id": r.context_packet_id,
        "provider": r.provider, "model": r.model_name, "mode": r.mode,
        "thinking_enabled": r.thinking_enabled, "status": r.status,
        "fallback_used": r.fallback_used, "latency_ms": r.latency_ms,
        "created_at": r.created_at,
    } for r in rows]

@router.get("/runs/{run_id}")
def run_detail(run_id: str, db: Session = Depends(get_db)):
    r = db.get(IntelligenceRun, run_id)
    if r is None:
        raise HTTPException(404, detail="intelligence run not found")
    return {
        "id": r.id, "context_packet_id": r.context_packet_id,
        "provider": r.provider, "model": r.model_name, "mode": r.mode,
        "thinking_enabled": r.thinking_enabled, "status": r.status,
        "fallback_used": r.fallback_used, "latency_ms": r.latency_ms,
        "request": r.request_json, "answer": r.response_json,
        "validation": r.validation_json, "created_at": r.created_at,
        "completed_at": r.completed_at,
    }
