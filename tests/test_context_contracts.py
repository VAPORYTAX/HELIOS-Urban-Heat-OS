import pytest
from pydantic import ValidationError
from app.contextforge.contracts import ContextBuildRequest
def test_context_budget_lower_bound():
    with pytest.raises(ValidationError): ContextBuildRequest(area_id="x",user_intent="hello",token_budget=100)
def test_valid_context_request():
    assert ContextBuildRequest(area_id="x",user_intent="prioritize cooling investments").mode=="planning"
