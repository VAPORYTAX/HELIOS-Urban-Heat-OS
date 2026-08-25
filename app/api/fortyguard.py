from fastapi import APIRouter, HTTPException

from app.fortyguard.client import FortyGuardClient
from app.fortyguard.exceptions import (
    FortyGuardAccessError,
    FortyGuardConfigurationError,
    FortyGuardRequestError,
    FortyGuardTimeoutError,
)
from app.fortyguard.schemas import (
    ActivityResult,
    ActivitySubmission,
    EnvironmentalParametersRequest,
    HeatmapRequest,
    SatelliteRequest,
    StreetViewRequest,
)

router = APIRouter(prefix="/provider/fortyguard", tags=["fortyguard"])

def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, FortyGuardConfigurationError):
        return HTTPException(status_code=503, detail=str(exc))
    if isinstance(exc, FortyGuardAccessError):
        return HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, FortyGuardTimeoutError):
        return HTTPException(status_code=504, detail=str(exc))
    if isinstance(exc, FortyGuardRequestError):
        return HTTPException(
            status_code=exc.status_code if exc.status_code and exc.status_code < 600 else 502,
            detail={"message": str(exc), "provider_payload": exc.payload},
        )
    return HTTPException(status_code=502, detail=str(exc))

@router.post("/heatmap", response_model=ActivitySubmission)
async def submit_heatmap(body: HeatmapRequest):
    try:
        return await FortyGuardClient().submit_heatmap(body)
    except Exception as exc:
        raise _translate(exc) from exc

@router.post("/streetview", response_model=ActivitySubmission)
async def submit_streetview(body: StreetViewRequest):
    try:
        return await FortyGuardClient().submit_streetview(body)
    except Exception as exc:
        raise _translate(exc) from exc

@router.post("/satellite", response_model=ActivitySubmission)
async def submit_satellite(body: SatelliteRequest):
    try:
        return await FortyGuardClient().submit_satellite(body)
    except Exception as exc:
        raise _translate(exc) from exc

@router.post("/environment", response_model=ActivitySubmission)
async def submit_environment(body: EnvironmentalParametersRequest):
    try:
        return await FortyGuardClient().submit_environmental_parameters(body)
    except Exception as exc:
        raise _translate(exc) from exc

@router.get("/activities/{activity_id}", response_model=ActivityResult)
async def activity(activity_id: str):
    try:
        return await FortyGuardClient().get_activity(activity_id, bypass_cache=True)
    except Exception as exc:
        raise _translate(exc) from exc

@router.get("/activities/{activity_id}/wait", response_model=ActivityResult)
async def wait_activity(activity_id: str):
    try:
        return await FortyGuardClient().wait_for_activity(activity_id)
    except Exception as exc:
        raise _translate(exc) from exc
