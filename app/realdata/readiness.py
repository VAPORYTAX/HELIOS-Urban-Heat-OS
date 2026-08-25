from app.config import get_settings
from app.realdata.census import status as census_status

def provider_readiness():
    settings = get_settings()
    return {
        "fortyguard": {
            "configured": bool(getattr(settings, "fortyguard_api_key", None)),
            "role": "primary thermal provider",
            "truth_category_when_live": "provider",
        },
        "openstreetmap": {
            "configured": True,
            "role": "urban form + facilities",
            "truth_category_when_live": "observed",
            "authentication": "none",
        },
        "census": census_status(),
    }
