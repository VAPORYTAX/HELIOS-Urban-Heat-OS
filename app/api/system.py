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

    # Gemma is an optional explanation/orchestration layer. Deterministic
    # spatial and numerical engines remain production-ready when it is
    # intentionally disabled.
    intelligence_ready = not gemma.get("enabled", False) or gemma.get("reachable", False)
    overall = "ready" if db_ok and intelligence_ready else "degraded"

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
            "model": gemma.get("model"),
            "fast_transport": "lmstudio_native",
            "fast_reasoning": "off",
            "firewall": "enabled",
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
            "gemma4": gemma_readiness().get("enabled", False),
            "thermalway": True,
            "thermal_accessibility": True,
            "critical_journeys": True,
            "decision_science": True,
        },
        "thermalway": {
            "algorithms": ["astar", "dijkstra", "yen_k_shortest"],
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
