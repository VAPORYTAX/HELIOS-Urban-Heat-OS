import pytest
from pydantic import ValidationError
from app.optimizer.schemas import OptimizationRequest

def test_invalid_confidence_rejected():
    with pytest.raises(ValidationError):
        OptimizationRequest(area_id="x", budget=100, min_confidence=1.2)

def test_objectives_supported():
    for name in ("max_teu","max_vulnerable_teu","max_people","max_roi","balanced"):
        r = OptimizationRequest(area_id="x", budget=100, objective=name)
        assert r.objective == name
