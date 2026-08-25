from app.optimizer.engine import CandidateValue, solve_portfolio

def c(i, cell, cost, teu, vuln, people, conf=0.9, months=2, feasible=True, category="x"):
    return CandidateValue(
        candidate_id=i,
        cell_id=cell,
        intervention_id=i,
        category=category,
        cost=cost,
        teu_benefit=teu,
        vulnerable_teu_benefit=vuln,
        people_benefit=people,
        confidence=conf,
        implementation_months=months,
        feasible=feasible,
    )

def test_budget_is_respected():
    rows = [
        c("a","c1",60,80,20,30),
        c("b","c2",60,70,25,40),
        c("c","c3",40,30,10,20),
    ]
    out = solve_portfolio(
        rows, budget=100, objective="max_teu", min_confidence=0,
        max_implementation_months=None, max_interventions_per_cell=2,
        min_vulnerable_benefit_share=0, require_feasible=True
    )
    assert out["total_cost"] <= 100
    assert out["estimated_teu_benefit"] >= 80

def test_confidence_gate():
    rows = [
        c("a","c1",20,100,50,50,conf=0.4),
        c("b","c2",20,50,25,25,conf=0.9),
    ]
    out = solve_portfolio(
        rows, budget=100, objective="max_teu", min_confidence=0.7,
        max_implementation_months=None, max_interventions_per_cell=2,
        min_vulnerable_benefit_share=0, require_feasible=True
    )
    assert [x.candidate_id for x in out["selected"]] == ["b"]

def test_time_gate():
    rows = [
        c("slow","c1",20,100,50,50,months=24),
        c("fast","c2",20,50,25,25,months=3),
    ]
    out = solve_portfolio(
        rows, budget=100, objective="max_teu", min_confidence=0,
        max_implementation_months=6, max_interventions_per_cell=2,
        min_vulnerable_benefit_share=0, require_feasible=True
    )
    assert [x.candidate_id for x in out["selected"]] == ["fast"]

def test_one_per_category_per_cell():
    rows = [
        c("a","c1",20,100,50,50,category="materials"),
        c("b","c1",20,90,45,45,category="materials"),
    ]
    out = solve_portfolio(
        rows, budget=100, objective="max_teu", min_confidence=0,
        max_implementation_months=None, max_interventions_per_cell=2,
        min_vulnerable_benefit_share=0, require_feasible=True
    )
    assert len(out["selected"]) == 1
