from datetime import datetime
from typing import Any,Literal
from pydantic import BaseModel,Field,field_validator
SourceType=Literal['observed','provider','fixture','derived','modelled','assumed']
class ThermalObservationIn(BaseModel):
    cell_id:str; observed_at:datetime; temperature_c:float=Field(ge=-90,le=80); apparent_temperature_c:float|None=Field(default=None,ge=-100,le=100); humidity_pct:float|None=Field(default=None,ge=0,le=100); heat_index_c:float|None=Field(default=None,ge=-100,le=120); source_type:SourceType; source_name:str; source_activity_id:str|None=None; quality_label:str='observed'; metadata:dict[str,Any]={}
class ThermalCellIn(BaseModel):
    id:str; area_id:str; grid_key:str; resolution_m:int=Field(ge=10,le=1000); geometry:dict[str,Any]
    @field_validator('geometry')
    @classmethod
    def polygon_only(cls,v):
        if v.get('type')!='Polygon': raise ValueError('thermal cell geometry must be GeoJSON Polygon')
        return v
