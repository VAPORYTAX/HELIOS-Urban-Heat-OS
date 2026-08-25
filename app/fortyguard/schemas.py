from enum import Enum
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class HeatmapAnalytic(str, Enum):
    TCM = "tcm"
    TIME_OF_MEASURE = "time_of_measure"
    EXCEEDANCE = "exceedance"
    PERSISTENCE = "persistence"

class FortyGuardDateTime(BaseModel):
    start_date: str
    filter_type: Literal[1, 2, 3, 4]
    start_time: str | None = None
    end_time: str | None = None
    end_date: str | None = None

    @model_validator(mode="after")
    def validate_filter_contract(self):
        if self.filter_type in (1, 2) and not self.start_time:
            raise ValueError("start_time is required for filter_type 1 or 2")
        if self.filter_type == 2 and not self.end_time:
            raise ValueError("end_time is required for filter_type 2")
        if self.filter_type == 4 and not self.end_date:
            raise ValueError("end_date is required for filter_type 4")
        return self

HeatmapDateTime = FortyGuardDateTime

class HeatmapRequest(BaseModel):
    polygon_aoi: dict[str, Any]
    date_time: FortyGuardDateTime
    granularity: Literal[60, 80, 100] = 100
    analytic_type: HeatmapAnalytic = HeatmapAnalytic.TCM
    threshold: float | None = None
    direction: Literal["above", "below"] = "above"

    @field_validator("polygon_aoi")
    @classmethod
    def validate_geojson(cls, value):
        if value.get("type") != "FeatureCollection":
            raise ValueError("polygon_aoi must be a GeoJSON FeatureCollection")
        features = value.get("features") or []
        if not features:
            raise ValueError("polygon_aoi must contain at least one feature")
        for feature in features:
            geometry = (feature or {}).get("geometry") or {}
            if geometry.get("type") != "Polygon":
                raise ValueError("every AOI feature must contain Polygon geometry")
            coordinates = geometry.get("coordinates") or []
            if not coordinates or len(coordinates[0]) < 4:
                raise ValueError("Polygon must contain a valid exterior ring")
            ring = coordinates[0]
            if ring[0] != ring[-1]:
                raise ValueError("Polygon exterior ring must be closed")
        return value

class StreetViewRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    vertical_angle: float
    horizontal_angle: float = Field(ge=0, le=360)
    back_view: bool = False

class SatelliteCoordinates(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

class SatelliteRequest(BaseModel):
    sat: SatelliteCoordinates
    date_time: FortyGuardDateTime
    granularity: Literal[60, 80, 100] = 80

    @model_validator(mode="after")
    def provider_filter_support(self):
        if self.date_time.filter_type == 4:
            raise ValueError("Satellite segmentation currently supports filter_type 1, 2, or 3")
        return self

class EnvironmentalParametersRequest(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    temperature: float
    date_time: FortyGuardDateTime
    parameters: list[str] | None = None

    @model_validator(mode="after")
    def provider_filter_support(self):
        if self.date_time.filter_type == 4:
            raise ValueError("Environmental Parameters currently supports filter_type 1, 2, or 3")
        return self

class ActivitySubmission(BaseModel):
    activity_id: str
    operation: str

class ActivityResult(BaseModel):
    activity_id: str
    status: str
    result: dict[str, Any] | None = None
    raw: dict[str, Any]
