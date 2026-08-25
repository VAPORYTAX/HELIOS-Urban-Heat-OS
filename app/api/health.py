from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.db.session import engine
from app.fortyguard.exceptions import FortyGuardConfigurationError
from app.fortyguard.client import FortyGuardClient

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except SQLAlchemyError:
        db_ok = False

    return {
        "service": "HELIOS",
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "unavailable",
        "environment": get_settings().helios_env,
    }

@router.get("/provider/fortyguard/health")
async def fortyguard_health():
    settings = get_settings()
    configured = bool(settings.fortyguard_api_key)
    return {
        "provider": "FortyGuard Temperature API",
        "configured": configured,
        "base_url": settings.fortyguard_base_url,
        "contract_version": "v1",
        "note": (
            "API key is configured. Use the smoke-test script for a live provider request."
            if configured
            else "Set FORTYGUARD_API_KEY in .env before live requests."
        ),
    }
