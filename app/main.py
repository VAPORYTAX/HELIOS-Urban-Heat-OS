from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.fortyguard import router as fortyguard_router
from app.api.health import router as health_router
from app.api.cities import router as cities_router
from app.api.thermal import router as thermal_router
from app.api.exposure import router as exposure_router
from app.api.interventions import router as interventions_router
from app.api.optimizer import router as optimizer_router
from app.api.agents import router as agents_router
from app.api.realdata import router as realdata_router
from app.api.demographics import router as demographics_router
from app.api.quality import router as quality_router
from app.api.contextforge import router as contextforge_router
from app.api.intelligence import router as intelligence_router
from app.api.fortyguard_live import router as fortyguard_live_router
from app.api.fortyguard_history import router as fortyguard_history_router
from app.api.provider_ops import router as provider_ops_router
from app.api.thermalway import router as thermalway_router
from app.api.thermalway_intelligence import router as thermalway_intelligence_router
from app.api.thermalway_accessibility import router as thermalway_accessibility_router
from app.api.system import router as system_router
from app.api.spatial import router as spatial_router
from app.config import get_settings
from app.logging import configure_logging

configure_logging()
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="HELIOS API",
    version="0.1.0",
    description="Urban thermal intelligence, counterfactual intervention and optimization platform.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.helios_api_prefix)
app.include_router(fortyguard_router, prefix=settings.helios_api_prefix)
app.include_router(cities_router, prefix=settings.helios_api_prefix)
app.include_router(thermal_router, prefix=settings.helios_api_prefix)
app.include_router(exposure_router, prefix=settings.helios_api_prefix)
app.include_router(interventions_router, prefix=settings.helios_api_prefix)
app.include_router(optimizer_router, prefix=settings.helios_api_prefix)
app.include_router(agents_router, prefix=settings.helios_api_prefix)
app.include_router(realdata_router, prefix=settings.helios_api_prefix)
app.include_router(demographics_router, prefix=settings.helios_api_prefix)
app.include_router(quality_router, prefix=settings.helios_api_prefix)
app.include_router(contextforge_router, prefix=settings.helios_api_prefix)
app.include_router(intelligence_router, prefix=settings.helios_api_prefix)
app.include_router(fortyguard_live_router, prefix=settings.helios_api_prefix)
app.include_router(fortyguard_history_router, prefix=settings.helios_api_prefix)
app.include_router(provider_ops_router, prefix=settings.helios_api_prefix)
app.include_router(thermalway_router, prefix=settings.helios_api_prefix)
app.include_router(thermalway_intelligence_router, prefix=settings.helios_api_prefix)
app.include_router(thermalway_accessibility_router, prefix=settings.helios_api_prefix)
app.include_router(system_router, prefix=settings.helios_api_prefix)
app.include_router(spatial_router, prefix=settings.helios_api_prefix)

@app.get("/")
def root():
    return {
        "name": "HELIOS",
        "release": "foundation",
        "api": settings.helios_api_prefix,
        "docs": "/docs",
    }
