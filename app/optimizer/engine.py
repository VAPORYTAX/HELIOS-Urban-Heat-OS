from __future__ import annotations
from dataclasses import dataclass

from ortools.sat.python import cp_model

SCALE = 1000

@dataclass(frozen=True)
class CandidateValue:
    candidate_id: str
    cell_id: str
    intervention_id: str
    category: str
    cost: float
    teu_benefit: float
    vulnerable_teu_benefit: float
    people_benefit: float
    confidence: float
    implementation_months: float
    feasible: bool

def _int(v: float) -> int:
    return int(round(float(v) * SCALE))

def objective_score(c: CandidateValue, objective: str) -> float:
    if objective == "max_teu":
        return c.teu_benefit
    if objective == "max_vulnerable_teu":
        return c.vulnerable_teu_benefit
    if objective == "max_people":
        return c.people_benefit
    if objective == "max_roi":
        return 0.0 if c.cost <= 0 else (c.teu_benefit / c.cost) * 100000.0
    # Balanced prioritizes total burden, vulnerable burden, people, and confidence.
    return (
        0.45 * c.teu_benefit
        + 0.35 * c.vulnerable_teu_benefit
        + 0.15 * c.people_benefit
        + 0.05 * (100.0 * c.confidence)
    )

def solve_portfolio(
    candidates: list[CandidateValue],
    *,
    budget: float,
    objective: str,
    min_confidence: float,
    max_implementation_months: float | None,
    max_interventions_per_cell: int,
    min_vulnerable_benefit_share: float,
    require_feasible: bool = True,
):
    eligible = [
        c for c in candidates
        if c.confidence >= min_confidence
        and (max_implementation_months is None or c.implementation_months <= max_implementation_months)
        and (c.feasible or not require_feasible)
    ]

    if not eligible:
        return {"status": "INFEASIBLE", "selected": [], "objective_value": 0.0}

    model = cp_model.CpModel()
    x = {c.candidate_id: model.NewBoolVar(f"x_{i}") for i, c in enumerate(eligible)}

    model.Add(
        sum(_int(c.cost) * x[c.candidate_id] for c in eligible)
        <= _int(budget)
    )

    by_cell: dict[str, list[CandidateValue]] = {}
    by_cell_category: dict[tuple[str, str], list[CandidateValue]] = {}
    for c in eligible:
        by_cell.setdefault(c.cell_id, []).append(c)
        by_cell_category.setdefault((c.cell_id, c.category), []).append(c)

    for rows in by_cell.values():
        model.Add(sum(x[c.candidate_id] for c in rows) <= max_interventions_per_cell)

    # Avoid selecting multiple materially similar treatments from the same category in one cell.
    for rows in by_cell_category.values():
        model.Add(sum(x[c.candidate_id] for c in rows) <= 1)

    if min_vulnerable_benefit_share > 0:
        vuln = sum(_int(c.vulnerable_teu_benefit) * x[c.candidate_id] for c in eligible)
        total = sum(
            _int(c.teu_benefit + c.vulnerable_teu_benefit) * x[c.candidate_id]
            for c in eligible
        )
        ratio_scaled = int(round(min_vulnerable_benefit_share * SCALE))
        # SCALE * vulnerable_benefit >= ratio * combined_benefit
        model.Add(SCALE * vuln >= ratio_scaled * total)

    scores = {_c.candidate_id: objective_score(_c, objective) for _c in eligible}
    model.Maximize(sum(_int(scores[c.candidate_id]) * x[c.candidate_id] for c in eligible))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10.0
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)

    name = solver.StatusName(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": name, "selected": [], "objective_value": 0.0}

    selected = [c for c in eligible if solver.Value(x[c.candidate_id]) == 1]
    return {
        "status": name,
        "selected": selected,
        "objective_value": sum(scores[c.candidate_id] for c in selected),
        "total_cost": sum(c.cost for c in selected),
        "estimated_teu_benefit": sum(c.teu_benefit for c in selected),
        "estimated_vulnerable_teu_benefit": sum(c.vulnerable_teu_benefit for c in selected),
        "estimated_people_benefit": sum(c.people_benefit for c in selected),
    }
