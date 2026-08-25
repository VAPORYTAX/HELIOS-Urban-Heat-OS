import pytest
from pydantic import ValidationError
from app.fortyguard.schemas import HeatmapDateTime, HeatmapRequest

def aoi(closed=True):
    ring = [
        [-112.0785, 33.4455],
        [-112.0655, 33.4455],
        [-112.0655, 33.4555],
        [-112.0785, 33.4555],
    ]
    ring.append(ring[0] if closed else [-112.0780, 33.4450])
    return {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {}, "geometry": {
            "type": "Polygon", "coordinates": [ring]
        }}],
    }

def test_heatmap_contract_accepts_closed_polygon():
    body = HeatmapRequest(
        polygon_aoi=aoi(),
        date_time=HeatmapDateTime(
            start_date="2026-08-20",
            start_time="12:00",
            filter_type=1,
        ),
        granularity=100,
    )
    assert body.granularity == 100

def test_heatmap_rejects_unclosed_polygon():
    with pytest.raises(ValidationError):
        HeatmapRequest(
            polygon_aoi=aoi(closed=False),
            date_time=HeatmapDateTime(
                start_date="2026-08-20",
                start_time="12:00",
                filter_type=1,
            ),
            granularity=100,
        )

def test_filter_two_requires_end_time():
    with pytest.raises(ValidationError):
        HeatmapDateTime(
            start_date="2026-08-20",
            start_time="12:00",
            filter_type=2,
        )

from app.fortyguard.schemas import (
    SatelliteCoordinates,
    SatelliteRequest,
    EnvironmentalParametersRequest,
)

def test_satellite_payload_contract():
    body = SatelliteRequest(
        sat=SatelliteCoordinates(latitude=33.45, longitude=-112.07),
        date_time=HeatmapDateTime(
            start_date="2026-08-20",
            start_time="12:00",
            filter_type=1,
        ),
        granularity=80,
    )
    payload = body.model_dump(mode="json")
    assert payload["sat"]["latitude"] == 33.45
    assert payload["granularity"] == 80

def test_environment_requires_temperature():
    body = EnvironmentalParametersRequest(
        latitude=33.45,
        longitude=-112.07,
        temperature=42.5,
        date_time=HeatmapDateTime(
            start_date="2026-08-20",
            start_time="12:00",
            filter_type=1,
        ),
    )
    assert body.temperature == 42.5
