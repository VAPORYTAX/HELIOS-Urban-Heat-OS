import httpx
import pytest

from app.config import Settings
from app.fortyguard.client import FortyGuardClient
from app.fortyguard.exceptions import FortyGuardAccessError
from app.fortyguard.schemas import HeatmapDateTime, HeatmapRequest

AOI = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-112.0785, 33.4455],
                [-112.0655, 33.4455],
                [-112.0655, 33.4555],
                [-112.0785, 33.4555],
                [-112.0785, 33.4455],
            ]],
        },
    }],
}

def settings():
    return Settings(
        database_url="sqlite://",
        fortyguard_api_key="test-key",
        fortyguard_base_url="https://api.fortyguard.com",
        fortyguard_max_retries=1,
    )

@pytest.mark.asyncio
async def test_submit_heatmap_extracts_activity_id():
    async def handler(request: httpx.Request):
        assert request.headers["api-key"] == "test-key"
        assert request.url.path == "/v1/heatmap"
        return httpx.Response(
            200,
            json={
                "error": False,
                "status_code": 200,
                "message": "Heatmap Submitted Successfully",
                "data": {"activity_id": "abc-123"},
            },
        )

    client = FortyGuardClient(settings(), transport=httpx.MockTransport(handler))
    req = HeatmapRequest(
        polygon_aoi=AOI,
        date_time=HeatmapDateTime(
            start_date="2026-08-20",
            start_time="12:00",
            filter_type=1,
        ),
        granularity=100,
    )
    out = await client.submit_heatmap(req)
    assert out.activity_id == "abc-123"
    assert out.operation == "heatmap"

@pytest.mark.asyncio
async def test_access_error_is_explicit():
    async def handler(request: httpx.Request):
        return httpx.Response(403, json={"message": "Premium required"})

    client = FortyGuardClient(settings(), transport=httpx.MockTransport(handler))
    with pytest.raises(FortyGuardAccessError):
        await client.get_activity("abc", bypass_cache=True)

@pytest.mark.asyncio
async def test_status_completed_result_parses():
    async def handler(request: httpx.Request):
        return httpx.Response(
            200,
            json={
                "error": False,
                "status_code": 200,
                "message": "Completed",
                "data": {
                    "activity_id": "abc",
                    "status": "Completed",
                    "result": {"map_data": {"type": "FeatureCollection", "features": []}},
                },
            },
        )
    client = FortyGuardClient(settings(), transport=httpx.MockTransport(handler))
    out = await client.get_activity("abc", bypass_cache=True)
    assert out.status == "Completed"
    assert out.result["map_data"]["type"] == "FeatureCollection"
