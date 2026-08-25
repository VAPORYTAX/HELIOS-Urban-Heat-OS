from __future__ import annotations
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.counterfactual.engine import simulate_cell
from app.db.models_exposure import ExposureMetric, UrbanContextCell
from app.db.models_interventions import (
    InterventionCandidate, InterventionCatalog, Scenario, ScenarioIntervention
)
from app.db.models_optimizer import OptimizationRun, OptimizationSelection
from app.db.models_thermal import ThermalCell
from app.interventions.service import generate_candidates, simulate_scenario
from app.optimizer.engine import CandidateValue, objective_score, solve_portfolio
from app.optimizer.schemas import OptimizationRequest

def candidate_values(db: Session, area_id: str) -> list[CandidateValue]:
    generate_candidates(db, area_id)
    cells = db.execute(select(ThermalCell).where(ThermalCell.area_id == area_id)).scalars().all()
    cell_map = {c.id: c for c in cells}

    values = []
    for cell_id in cell_map:
        exposure = db.execute(
            select(ExposureMetric)
            .where(ExposureMetric.cell_id == cell_id)
            .order_by(desc(ExposureMetric.observed_at))
            .limit(1)
        ).scalar_one_or_none()
        context = db.execute(
            select(UrbanContextCell).where(UrbanContextCell.cell_id == cell_id)
        ).scalar_one_or_none()
        if not exposure or not context:
            continue

        candidates = db.execute(
            select(InterventionCandidate).where(InterventionCandidate.cell_id == cell_id)
        ).scalars().all()

        for c in candidates:
            catalog = db.get(InterventionCatalog, c.intervention_id)
            if catalog is None:
                continue
            single = simulate_cell(
                baseline_teu=exposure.teu,
                baseline_vulnerable_teu=exposure.vulnerable_teu,
                interventions=[{
                    "effect_profile": catalog.effect_profile_json,
                    "suitability_score": c.suitability_score,
                    "confidence": c.confidence,
                }],
                base_confidence=exposure.confidence,
            )
            hazard_fraction = 0.0 if exposure.teu <= 0 else single["teu_reduction"] / exposure.teu
            people_benefit = context.population * hazard_fraction

            values.append(CandidateValue(
                candidate_id=c.id,
                cell_id=c.cell_id,
                intervention_id=c.intervention_id,
                category=catalog.category,
                cost=c.estimated_cost,
                teu_benefit=single["teu_reduction"],
                vulnerable_teu_benefit=single["vulnerable_teu_reduction"],
                people_benefit=people_benefit,
                confidence=min(c.confidence, exposure.confidence),
                implementation_months=c.implementation_months,
                feasible=bool(c.reasons_json.get("feasible")),
            ))
    return values

def run_optimization(db: Session, req: OptimizationRequest):
    run = OptimizationRun(
        area_id=req.area_id,
        objective=req.objective,
        status="running",
        budget=req.budget,
        min_confidence=req.min_confidence,
        max_implementation_months=req.max_implementation_months,
        max_interventions_per_cell=req.max_interventions_per_cell,
        min_vulnerable_benefit_share=req.min_vulnerable_benefit_share,
        config_json=req.model_dump(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    values = candidate_values(db, req.area_id)
    solved = solve_portfolio(
        values,
        budget=req.budget,
        objective=req.objective,
        min_confidence=req.min_confidence,
        max_implementation_months=req.max_implementation_months,
        max_interventions_per_cell=req.max_interventions_per_cell,
        min_vulnerable_benefit_share=req.min_vulnerable_benefit_share,
        require_feasible=req.require_feasible,
    )

    run.solver_status = solved["status"]
    if not solved["selected"]:
        run.status = "infeasible"
        run.objective_value = 0.0
        run.total_cost = 0.0
        run.selected_count = 0
        run.completed_at = datetime.now(timezone.utc)
        db.commit()
        return run, None

    scenario = Scenario(
        area_id=req.area_id,
        name=f"Optimized {req.objective} portfolio",
        status="ready",
        objective=req.objective,
        budget=req.budget,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    value_by_id = {v.candidate_id: v for v in values}
    for selected in solved["selected"]:
        db.add(ScenarioIntervention(
            scenario_id=scenario.id,
            candidate_id=selected.candidate_id,
            quantity=1.0,
            selected=True,
        ))
        db.add(OptimizationSelection(
            run_id=run.id,
            candidate_id=selected.candidate_id,
            cell_id=selected.cell_id,
            intervention_id=selected.intervention_id,
            cost=selected.cost,
            estimated_teu_benefit=selected.teu_benefit,
            estimated_vulnerable_teu_benefit=selected.vulnerable_teu_benefit,
            estimated_people_benefit=selected.people_benefit,
            confidence=selected.confidence,
            score_components_json={
                "objective": req.objective,
                "objective_score": objective_score(selected, req.objective),
                "category": selected.category,
                "implementation_months": selected.implementation_months,
            },
        ))

    db.commit()
    result = simulate_scenario(db, scenario.id)

    run.scenario_id = scenario.id
    run.status = "complete"
    run.objective_value = solved["objective_value"]
    run.total_cost = result.total_cost
    run.selected_count = len(solved["selected"])
    run.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run, result

def run_pareto(db: Session, area_id: str, budget: float, min_confidence: float,
               max_implementation_months: float | None, max_interventions_per_cell: int):
    outputs = []
    for objective in ("max_teu", "max_vulnerable_teu", "max_people", "max_roi", "balanced"):
        req = OptimizationRequest(
            area_id=area_id,
            budget=budget,
            objective=objective,
            min_confidence=min_confidence,
            max_implementation_months=max_implementation_months,
            max_interventions_per_cell=max_interventions_per_cell,
            min_vulnerable_benefit_share=0.0,
            require_feasible=True,
        )
        run, result = run_optimization(db, req)
        outputs.append({
            "run_id": run.id,
            "scenario_id": run.scenario_id,
            "objective": objective,
            "status": run.status,
            "solver_status": run.solver_status,
            "selected_count": run.selected_count,
            "total_cost": run.total_cost,
            "teu_reduction": result.teu_reduction if result else 0.0,
            "vulnerable_teu_reduction": result.vulnerable_teu_reduction if result else 0.0,
            "thermal_roi": result.thermal_roi if result else 0.0,
            "confidence": result.confidence if result else 0.0,
        })
    return outputs
