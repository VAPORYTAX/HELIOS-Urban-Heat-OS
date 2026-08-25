from typing import Literal
from pydantic import BaseModel, Field
class ContextBuildRequest(BaseModel):
    area_id: str
    user_intent: str = Field(min_length=3,max_length=4000)
    mode: Literal["operational","planning","investment","design","evidence"]="planning"
    task_type: Literal["situation_assessment","intervention_planning","portfolio_optimization","scenario_comparison","evidence_review","executive_brief"]="intervention_planning"
    token_budget: int = Field(default=24000,ge=4000,le=200000)
    include_raw_evidence: bool=False
