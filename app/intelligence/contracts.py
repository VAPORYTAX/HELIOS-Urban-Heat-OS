from typing import Literal
from pydantic import BaseModel, Field

class IntelligenceQuery(BaseModel):
    area_id: str
    query: str = Field(min_length=3, max_length=5000)
    mode: Literal["operational","planning","investment","design","evidence"] = "planning"
    task_type: Literal[
        "situation_assessment","intervention_planning","portfolio_optimization",
        "scenario_comparison","evidence_review","executive_brief"
    ] = "intervention_planning"
    token_budget: int = Field(default=24000, ge=4000, le=200000)
    force_thinking: bool | None = None

class IntelligenceAnswer(BaseModel):
    decision_status: Literal["recommend","review_required","blocked","informational"]
    headline: str
    summary: str
    recommended_actions: list[dict] = []
    uncertainties: list[str] = []
    evidence_refs: list[str] = []
    numeric_claims: dict[str, float] = {}
    requires_human_review: bool
