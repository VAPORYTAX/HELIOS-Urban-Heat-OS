from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_interventions import InterventionCandidate, InterventionCatalog, Scenario, ScenarioResult
from app.db.models_provider_decision import ProviderInterventionCandidate, ProviderOptimizerRun
from app.db.session import get_db
from app.interventions.service import generate_candidates, simulate_scenario

router = APIRouter(tags=["interventions"])

@router.get("/interventions/catalog")
def catalog(db: Session = Depends(get_db)):
    rows = db.execute(select(InterventionCatalog).order_by(InterventionCatalog.name)).scalars().all()
    return [{
        "id": r.id,
        "name": r.name,
        "category": r.category,
        "description": r.description,
        "effect_profile": r.effect_profile_json,
        "cost_model": r.cost_model_json,
        "constraints": r.constraints_json,
        "evidence_level": r.evidence_level,
        "base_confidence": r.base_confidence,
    } for r in rows]

@router.post("/interventions/candidates/generate")
def generate(area_id: str, db: Session = Depends(get_db)):
    rows = generate_candidates(db, area_id)
    return {"area_id": area_id, "candidate_count": len(rows)}

@router.get("/interventions/candidates")
def candidates(area_id: str, db: Session = Depends(get_db)):
    from app.db.models_thermal import ThermalCell
    cell_ids = db.execute(select(ThermalCell.id).where(ThermalCell.area_id == area_id)).scalars().all()
    rows = db.execute(
        select(InterventionCandidate).where(InterventionCandidate.cell_id.in_(cell_ids))
    ).scalars().all()
    return [{
        "id": r.id,
        "cell_id": r.cell_id,
        "intervention_id": r.intervention_id,
        "suitability_score": r.suitability_score,
        "estimated_cost": r.estimated_cost,
        "implementation_months": r.implementation_months,
        "confidence": r.confidence,
        "feasible": bool(r.reasons_json.get("feasible")),
        "reasons": r.reasons_json,
        "constraints": r.constraints_json,
    } for r in rows]

@router.get("/interventions/provider-native/candidates")
def provider_native_candidates(area_id: str, db: Session = Depends(get_db)):
    run = db.execute(
        select(ProviderOptimizerRun).where(ProviderOptimizerRun.area_id == area_id)
        .order_by(desc(ProviderOptimizerRun.created_at)).limit(1)
    ).scalar_one_or_none()
    if run is None:
        raise HTTPException(404, detail="provider-native optimization run not found")
    selected = {x["candidate_id"] for x in run.selected_json}
    anchor = db.get(ProviderInterventionCandidate, next(iter(selected), ""))
    if anchor is None:
        raise HTTPException(409, detail="provider-native optimizer candidate evidence is incomplete")
    rows = db.execute(
        select(ProviderInterventionCandidate)
        .where(ProviderInterventionCandidate.run_id == anchor.run_id)
        .order_by(ProviderInterventionCandidate.cell_id, ProviderInterventionCandidate.intervention_type)
    ).scalars().all()
    return [{
        "id": r.id,
        "cell_id": r.cell_id,
        "intervention_type": r.intervention_type,
        "estimated_cost": r.cost,
        "temperature_delta_c": r.temperature_delta_c,
        "teu_reduction": r.teu_reduction,
        "va_teu_reduction": r.va_teu_reduction,
        "people_benefit_proxy": r.people_benefit_proxy,
        "feasibility": r.feasibility,
        "confidence": r.confidence,
        "selected": r.id in selected,
        "assumptions": r.assumption_json,
        "truth_category": "modelled_counterfactual",
    } for r in rows]

@router.get("/scenarios")
def scenarios(area_id: str, db: Session = Depends(get_db)):
    rows = db.execute(select(Scenario).where(Scenario.area_id == area_id).order_by(desc(Scenario.created_at))).scalars().all()
    return [{
        "id": r.id,
        "name": r.name,
        "status": r.status,
        "objective": r.objective,
        "budget": r.budget,
        "created_at": r.created_at,
    } for r in rows]

@router.post("/scenarios/{scenario_id}/simulate")
def simulate(scenario_id: str, db: Session = Depends(get_db)):
    try:
        r = simulate_scenario(db, scenario_id)
    except ValueError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    return {
        "scenario_id": scenario_id,
        "baseline_teu": r.baseline_teu,
        "projected_teu": r.projected_teu,
        "teu_reduction": r.teu_reduction,
        "teu_reduction_pct": r.teu_reduction_pct,
        "total_cost": r.total_cost,
        "thermal_roi": r.thermal_roi,
        "confidence": r.confidence,
        "lower_teu_reduction": r.lower_teu_reduction,
        "upper_teu_reduction": r.upper_teu_reduction,
    }

@router.get("/scenarios/{scenario_id}/result")
def result(scenario_id: str, db: Session = Depends(get_db)):
    r = db.execute(select(ScenarioResult).where(ScenarioResult.scenario_id == scenario_id)).scalar_one_or_none()
    if r is None:
        raise HTTPException(404, detail="scenario result not found")
    return {
        "scenario_id": r.scenario_id,
        "baseline_teu": r.baseline_teu,
        "projected_teu": r.projected_teu,
        "teu_reduction": r.teu_reduction,
        "teu_reduction_pct": r.teu_reduction_pct,
        "baseline_vulnerable_teu": r.baseline_vulnerable_teu,
        "projected_vulnerable_teu": r.projected_vulnerable_teu,
        "vulnerable_teu_reduction": r.vulnerable_teu_reduction,
        "total_cost": r.total_cost,
        "thermal_roi": r.thermal_roi,
        "confidence": r.confidence,
        "uncertainty_interval": [r.lower_teu_reduction, r.upper_teu_reduction],
        "assumptions": r.assumptions_json,
        "cell_results": r.cell_results_json,
    }
