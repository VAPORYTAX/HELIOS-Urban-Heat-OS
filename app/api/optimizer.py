from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_optimizer import OptimizationRun, OptimizationSelection
from app.db.models_provider_decision import ProviderAgentDecision, ProviderOptimizerRun
from app.db.models_interventions import ScenarioResult
from app.db.session import get_db
from app.optimizer.schemas import OptimizationRequest, ParetoRequest
from app.optimizer.service import run_optimization, run_pareto

router = APIRouter(prefix="/optimizer", tags=["optimizer"])

def serialize_provider_run(db: Session, run: ProviderOptimizerRun):
    decision = db.execute(
        select(ProviderAgentDecision)
        .where(ProviderAgentDecision.optimizer_run_id == run.id)
        .order_by(desc(ProviderAgentDecision.created_at))
        .limit(1)
    ).scalar_one_or_none()
    return {
        "id": run.id,
        "area_id": run.area_id,
        "objective": run.objective,
        "status": run.status,
        "solver_status": run.status.upper(),
        "budget": run.budget,
        "total_cost": run.total_cost,
        "selected_count": len(run.selected_json),
        "teu_reduction": run.teu_reduction,
        "va_teu_reduction": run.va_teu_reduction,
        "confidence": run.confidence,
        "selections": run.selected_json,
        "source_metric_ids": run.source_metric_ids,
        "truth_category": "modelled_provider_decision",
        "requires_human_review": True if decision is None else decision.requires_human_review,
        "decision_status": "review_required" if decision is None else decision.status,
        "created_at": run.created_at,
    }

def serialize_run(db: Session, run: OptimizationRun):
    selections = db.execute(
        select(OptimizationSelection).where(OptimizationSelection.run_id == run.id)
    ).scalars().all()
    scenario_result = None
    if run.scenario_id:
        scenario_result = db.execute(
            select(ScenarioResult).where(ScenarioResult.scenario_id == run.scenario_id)
        ).scalar_one_or_none()
    return {
        "id": run.id,
        "area_id": run.area_id,
        "scenario_id": run.scenario_id,
        "objective": run.objective,
        "status": run.status,
        "solver_status": run.solver_status,
        "budget": run.budget,
        "total_cost": run.total_cost,
        "selected_count": run.selected_count,
        "objective_value": run.objective_value,
        "constraints": {
            "min_confidence": run.min_confidence,
            "max_implementation_months": run.max_implementation_months,
            "max_interventions_per_cell": run.max_interventions_per_cell,
            "min_vulnerable_benefit_share": run.min_vulnerable_benefit_share,
        },
        "selections": [{
            "candidate_id": s.candidate_id,
            "cell_id": s.cell_id,
            "intervention_id": s.intervention_id,
            "cost": s.cost,
            "estimated_teu_benefit": s.estimated_teu_benefit,
            "estimated_vulnerable_teu_benefit": s.estimated_vulnerable_teu_benefit,
            "estimated_people_benefit": s.estimated_people_benefit,
            "confidence": s.confidence,
            "score_components": s.score_components_json,
        } for s in selections],
        "scenario_result": None if scenario_result is None else {
            "baseline_teu": scenario_result.baseline_teu,
            "projected_teu": scenario_result.projected_teu,
            "teu_reduction": scenario_result.teu_reduction,
            "teu_reduction_pct": scenario_result.teu_reduction_pct,
            "vulnerable_teu_reduction": scenario_result.vulnerable_teu_reduction,
            "thermal_roi": scenario_result.thermal_roi,
            "confidence": scenario_result.confidence,
            "uncertainty_interval": [
                scenario_result.lower_teu_reduction,
                scenario_result.upper_teu_reduction,
            ],
        },
    }

@router.post("/run")
def optimize(body: OptimizationRequest, db: Session = Depends(get_db)):
    run, _ = run_optimization(db, body)
    return serialize_run(db, run)

@router.get("/runs")
def list_runs(area_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        select(OptimizationRun)
        .where(OptimizationRun.area_id == area_id)
        .order_by(desc(OptimizationRun.created_at))
    ).scalars().all()
    return [{
        "id": r.id,
        "scenario_id": r.scenario_id,
        "objective": r.objective,
        "status": r.status,
        "solver_status": r.solver_status,
        "budget": r.budget,
        "total_cost": r.total_cost,
        "selected_count": r.selected_count,
        "created_at": r.created_at,
    } for r in rows]

@router.get("/provider-native/latest")
def latest_provider_native(area_id: str, db: Session = Depends(get_db)):
    run = db.execute(
        select(ProviderOptimizerRun)
        .where(ProviderOptimizerRun.area_id == area_id)
        .order_by(desc(ProviderOptimizerRun.created_at))
        .limit(1)
    ).scalar_one_or_none()
    if run is None:
        raise HTTPException(404, detail="provider-native optimization run not found")
    return serialize_provider_run(db, run)

@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.get(OptimizationRun, run_id)
    if run is None:
        raise HTTPException(404, detail="optimization run not found")
    return serialize_run(db, run)

@router.post("/pareto")
def pareto(body: ParetoRequest, db: Session = Depends(get_db)):
    rows = run_pareto(
        db,
        area_id=body.area_id,
        budget=body.budget,
        min_confidence=body.min_confidence,
        max_implementation_months=body.max_implementation_months,
        max_interventions_per_cell=body.max_interventions_per_cell,
    )
    return {"area_id": body.area_id, "budget": body.budget, "portfolios": rows}
