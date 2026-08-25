from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from sqlalchemy import text

from app.db.session import SessionLocal
from app.intelligence.gateway import readiness as gemma_readiness

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status")
def system_status(request: Request):
    db_ok = False
    db_error = None
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        db_error = str(exc)
    finally:
        db.close()

    gemma = gemma_readiness()
    route_count = len(request.app.routes)

    # HELIOS deterministic/spatial decision engines are operational when the
    # database is healthy. Gemma is an optional explanation/orchestration
    # layer and must never become a single point of failure for core truth.
    overall = "ready" if db_ok else "degraded"
    intelligence_state = (
        "ready"
        if gemma.get("enabled") and gemma.get("reachable")
        else "unavailable"
        if gemma.get("enabled")
        else "disabled"
    )

    return {
        "status": overall,
        "service": "HELIOS",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "database": {
            "ready": db_ok,
            "error": db_error,
        },
        "intelligence": {
            "enabled": gemma.get("enabled", False),
            "reachable": gemma.get("reachable", False),
            "state": intelligence_state,
            "model": gemma.get("model"),
            "fast_transport": "lmstudio_native" if gemma.get("reachable") else None,
            "fast_reasoning": "off",
            "firewall": "enabled",
            "role": "explanation_and_orchestration_only",
            "core_decision_engines_depend_on_ai": False,
        },
        "api": {
            "route_count": route_count,
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
        "truth_policy": {
            "prediction_claims": False,
            "modelled_is_causal": False,
            "human_review_gate": True,
        },
    }


@router.get("/capabilities")
def capabilities():
    return {
        "modes": ["command", "planning", "investment", "design", "evidence"],
        "engines": {
            "thermal_intelligence": True,
            "provider_operations": True,
            "counterfactual_interventions": True,
            "portfolio_optimizer": True,
            "governed_agents": True,
            "contextforge": True,
            "gemma4": True,
            "thermalway": True,
            "thermal_accessibility": True,
            "critical_journeys": True,
            "decision_science": True,
        },
        "thermalway": {
            "algorithms": ["astar", "dijkstra", "yen_k_shortest"],
            "modes": ["fastest", "cool", "warm", "thermal_safe"],
            "profiles": [
                "standard",
                "child",
                "older_adult",
                "outdoor_worker",
                "mobility_limited",
            ],
            "truth_category": "real_osm_provider_thermal_modelled_cost",
        },
    }
