from datetime import datetime, timezone
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session

from app.db.models_exposure import DriverAttribution, ExposureMetric, UrbanContextCell
from app.db.models_interventions import (
    InterventionCandidate, InterventionCatalog, Scenario,
    ScenarioIntervention, ScenarioResult
)
from app.db.models_thermal import ThermalCell
from app.interventions.catalog import INTERVENTIONS
from app.interventions.engine import estimate_cost, suitability
from app.counterfactual.engine import simulate_cell

def seed_catalog(db: Session):
    for item in INTERVENTIONS:
        row = db.get(InterventionCatalog, item["id"])
        if row is None:
            row = InterventionCatalog(id=item["id"])
            db.add(row)
        row.name = item["name"]
        row.category = item["category"]
        row.description = item["description"]
        row.effect_profile_json = item["effect_profile"]
        row.cost_model_json = item["cost_model"]
        row.constraints_json = item["constraints"]
        row.evidence_level = item["evidence_level"]
        row.base_confidence = item["base_confidence"]
        row.active = True
    db.commit()

def generate_candidates(db: Session, area_id: str):
    seed_catalog(db)
    cells = db.execute(select(ThermalCell).where(ThermalCell.area_id == area_id)).scalars().all()
    catalog = db.execute(select(InterventionCatalog).where(InterventionCatalog.active.is_(True))).scalars().all()

    out = []
    for cell in cells:
        context = db.execute(select(UrbanContextCell).where(UrbanContextCell.cell_id == cell.id)).scalar_one_or_none()
        driver = db.execute(
            select(DriverAttribution)
            .where(DriverAttribution.cell_id == cell.id)
            .order_by(desc(DriverAttribution.observed_at))
            .limit(1)
        ).scalar_one_or_none()
        if not context:
            continue

        for catalog_row in catalog:
            item = {
                "id": catalog_row.id,
                "constraints": catalog_row.constraints_json,
                "base_confidence": catalog_row.base_confidence,
                "cost_model": catalog_row.cost_model_json,
            }
            # implementation months is stored in canonical fixture catalog
            canonical = next(x for x in INTERVENTIONS if x["id"] == catalog_row.id)
            assessment = suitability(canonical, context, driver)
            existing = db.execute(
                select(InterventionCandidate).where(
                    InterventionCandidate.cell_id == cell.id,
                    InterventionCandidate.intervention_id == catalog_row.id,
                )
            ).scalar_one_or_none()
            if existing is None:
                existing = InterventionCandidate(cell_id=cell.id, intervention_id=catalog_row.id)
                db.add(existing)
            existing.suitability_score = assessment["suitability_score"]
            existing.estimated_cost = estimate_cost(canonical, assessment["suitability_score"])
            existing.implementation_months = canonical["implementation_months"]
            existing.confidence = assessment["confidence"]
            existing.reasons_json = {"reasons": assessment["reasons"], "feasible": assessment["feasible"]}
            existing.constraints_json = {"failures": assessment["constraint_failures"]}
            out.append(existing)
    db.commit()
    return out

def build_fixture_scenario(db: Session, area_id: str):
    candidates = generate_candidates(db, area_id)
    scenario = Scenario(
        area_id=area_id,
        name="HELIOS Balanced Cooling Portfolio",
        status="ready",
        objective="balanced",
        budget=120000,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    # Choose best feasible candidate per cell, then add a second complementary intervention
    by_cell = {}
    for c in candidates:
        feasible = bool(c.reasons_json.get("feasible"))
        if feasible:
            by_cell.setdefault(c.cell_id, []).append(c)

    selected = []
    for cell_id, rows in by_cell.items():
        ranked = sorted(rows, key=lambda x: (x.suitability_score, x.confidence), reverse=True)
        for candidate in ranked[:2]:
            if sum(x.estimated_cost for x in selected) + candidate.estimated_cost <= scenario.budget:
                selected.append(candidate)

    for c in selected:
        db.add(ScenarioIntervention(scenario_id=scenario.id, candidate_id=c.id, quantity=1.0, selected=True))
    db.commit()
    return scenario

def simulate_scenario(db: Session, scenario_id: str):
    scenario = db.get(Scenario, scenario_id)
    if scenario is None:
        raise ValueError("scenario not found")

    selections = db.execute(
        select(ScenarioIntervention).where(
            ScenarioIntervention.scenario_id == scenario_id,
            ScenarioIntervention.selected.is_(True),
        )
    ).scalars().all()

    candidate_ids = [x.candidate_id for x in selections]
    candidates = db.execute(
        select(InterventionCandidate).where(InterventionCandidate.id.in_(candidate_ids))
    ).scalars().all() if candidate_ids else []

    by_cell = {}
    total_cost = 0.0
    for candidate in candidates:
        catalog = db.get(InterventionCatalog, candidate.intervention_id)
        by_cell.setdefault(candidate.cell_id, []).append({
            "intervention_id": candidate.intervention_id,
            "effect_profile": catalog.effect_profile_json,
            "suitability_score": candidate.suitability_score,
            "confidence": candidate.confidence,
            "cost": candidate.estimated_cost,
        })
        total_cost += candidate.estimated_cost

    cells = db.execute(select(ThermalCell).where(ThermalCell.area_id == scenario.area_id)).scalars().all()
    cell_results = []
    baseline_teu = baseline_vuln = projected_teu = projected_vuln = 0.0
    lower = upper = 0.0
    confidences = []

    for cell in cells:
        exposure = db.execute(
            select(ExposureMetric)
            .where(ExposureMetric.cell_id == cell.id)
            .order_by(desc(ExposureMetric.observed_at))
            .limit(1)
        ).scalar_one_or_none()
        if not exposure:
            continue

        result = simulate_cell(
            baseline_teu=exposure.teu,
            baseline_vulnerable_teu=exposure.vulnerable_teu,
            interventions=by_cell.get(cell.id, []),
            base_confidence=exposure.confidence,
        )

        baseline_teu += exposure.teu
        baseline_vuln += exposure.vulnerable_teu
        projected_teu += result["projected_teu"]
        projected_vuln += result["projected_vulnerable_teu"]
        lower += result["lower_teu_reduction"]
        upper += result["upper_teu_reduction"]
        confidences.append(result["confidence"])
        cell_results.append({
            "cell_id": cell.id,
            "baseline_teu": exposure.teu,
            **result,
            "interventions": by_cell.get(cell.id, []),
        })

    reduction = max(0.0, baseline_teu - projected_teu)
    vuln_reduction = max(0.0, baseline_vuln - projected_vuln)
    roi = reduction / total_cost if total_cost > 0 else 0.0
    confidence = min(confidences) if confidences else 0.0

    row = db.execute(
        select(ScenarioResult).where(ScenarioResult.scenario_id == scenario_id)
    ).scalar_one_or_none()
    if row is None:
        row = ScenarioResult(scenario_id=scenario_id)
        db.add(row)

    row.baseline_teu = baseline_teu
    row.projected_teu = projected_teu
    row.teu_reduction = reduction
    row.teu_reduction_pct = (100.0 * reduction / baseline_teu) if baseline_teu else 0.0
    row.baseline_vulnerable_teu = baseline_vuln
    row.projected_vulnerable_teu = projected_vuln
    row.vulnerable_teu_reduction = vuln_reduction
    row.total_cost = total_cost
    row.thermal_roi = roi
    row.confidence = confidence
    row.lower_teu_reduction = lower
    row.upper_teu_reduction = upper
    row.assumptions_json = {
        "truth_category": "modelled",
        "method": "counterfactual-composition-v1",
        "note": "Operational scenario model; not a causal temperature guarantee.",
    }
    row.cell_results_json = {"cells": cell_results}
    row.computed_at = datetime.now(timezone.utc)
    scenario.status = "simulated"
    db.commit()
    db.refresh(row)
    return row
