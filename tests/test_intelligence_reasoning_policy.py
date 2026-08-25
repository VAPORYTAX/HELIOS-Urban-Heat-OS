from app.intelligence.router import choose_thinking

def test_force_false_wins():
    assert choose_thinking('portfolio_optimization','investment',False) is False

def test_portfolio_fast_default():
    assert choose_thinking('portfolio_optimization','investment',None) is False

def test_operational_fast():
    assert choose_thinking('scenario_comparison','operational',None) is False

def test_scenario_deep():
    assert choose_thinking('scenario_comparison','planning',None) is True

def test_exec_fast():
    assert choose_thinking('executive_brief','planning',None) is False
