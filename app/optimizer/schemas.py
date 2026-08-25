from typing import Literal
from pydantic import BaseModel, Field, model_validator

Objective = Literal["max_teu", "max_vulnerable_teu", "max_people", "max_roi", "balanced"]

class OptimizationRequest(BaseModel):
    area_id: str
    budget: float = Field(gt=0, le=1_000_000_000)
    objective: Objective = "balanced"
    min_confidence: float = Field(default=0.65, ge=0, le=1)
    max_implementation_months: float | None = Field(default=None, gt=0, le=120)
    max_interventions_per_cell: int = Field(default=2, ge=1, le=5)
    min_vulnerable_benefit_share: float = Field(default=0.0, ge=0, le=1)
    require_feasible: bool = True

    @model_validator(mode="after")
    def validate_budget(self):
        if self.budget < 1:
            raise ValueError("budget must be at least 1")
        return self

class ParetoRequest(BaseModel):
    area_id: str
    budget: float = Field(gt=0, le=1_000_000_000)
    min_confidence: float = Field(default=0.65, ge=0, le=1)
    max_implementation_months: float | None = Field(default=None, gt=0, le=120)
    max_interventions_per_cell: int = Field(default=2, ge=1, le=5)
