from typing import Literal
from pydantic import BaseModel, Field

class AgentDecisionRequest(BaseModel):
    area_id: str
    optimization_run_id: str | None = None
    mode: Literal["operational", "planning", "investment"] = "planning"
    min_recommendation_confidence: float = Field(default=0.70, ge=0, le=1)
    require_real_data_for_operational: bool = True
