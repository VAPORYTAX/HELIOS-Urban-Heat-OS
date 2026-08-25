import json
from app.db.session import SessionLocal
from app.optimizer.schemas import OptimizationRequest
from app.optimizer.service import run_optimization, run_pareto

db = SessionLocal()
try:
    req = OptimizationRequest(
        area_id="phx-downtown",
        budget=100000,
        objective="balanced",
        min_confidence=0.65,
        max_implementation_months=12,
        max_interventions_per_cell=2,
        min_vulnerable_benefit_share=0.20,
        require_feasible=True,
    )
    run, result = run_optimization(db, req)
    pareto = run_pareto(
        db,
        area_id="phx-downtown",
        budget=100000,
        min_confidence=0.65,
        max_implementation_months=12,
        max_interventions_per_cell=2,
    )
    print(json.dumps({
        "run_id": run.id,
        "scenario_id": run.scenario_id,
        "status": run.status,
        "solver_status": run.solver_status,
        "objective": run.objective,
        "budget": run.budget,
        "total_cost": run.total_cost,
        "selected_count": run.selected_count,
        "teu_reduction": result.teu_reduction if result else 0,
        "teu_reduction_pct": result.teu_reduction_pct if result else 0,
        "vulnerable_teu_reduction": result.vulnerable_teu_reduction if result else 0,
        "thermal_roi": result.thermal_roi if result else 0,
        "confidence": result.confidence if result else 0,
        "pareto": pareto,
    }, indent=2))
finally:
    db.close()
