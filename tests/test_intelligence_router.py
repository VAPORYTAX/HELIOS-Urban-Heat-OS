from app.intelligence.router import choose_model, choose_thinking

def test_operational_disables_thinking():
    assert choose_thinking("portfolio_optimization","operational",None) is False

def test_deep_task_enables_thinking():
    assert choose_thinking("scenario_comparison","planning",None) is True

def test_force_override():
    assert choose_thinking("situation_assessment","planning",True) is True

def test_model_router():
    cfg={"model":"deep","fallback_model":"fast"}
    assert choose_model("situation_assessment",cfg)=="fast"
    assert choose_model("portfolio_optimization",cfg)=="deep"

