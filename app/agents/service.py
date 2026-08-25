from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.agents.contracts import AgentDecisionRequest
from app.agents.engine import (
    diagnostician_agent, evidence_agent, executive_agent, exposure_agent,
    planner_agent, scout_agent, skeptic_agent
)
from app.db.models_agents import AgentFinding, AgentRun, EvidenceRecord, Recommendation
from app.db.models_exposure import DriverAttribution, ExposureMetric, UrbanContextCell
from app.db.models_optimizer import OptimizationRun, OptimizationSelection
from app.db.models_interventions import ScenarioResult
from app.db.models_thermal import ThermalHotspot, ThermalObservation, ThermalCell

def _latest_optimizer(db: Session, area_id: str, run_id: str | None):
    if run_id:
        run = db.get(OptimizationRun, run_id)
        if not run:
            raise ValueError("optimization run not found")
        return run
    return db.execute(
        select(OptimizationRun)
        .where(OptimizationRun.area_id == area_id, OptimizationRun.status == "complete")
        .order_by(desc(OptimizationRun.created_at))
        .limit(1)
    ).scalar_one_or_none()

def _area_exposure(db: Session, area_id: str):
    cell_ids = db.execute(select(ThermalCell.id).where(ThermalCell.area_id == area_id)).scalars().all()
    metrics = []
    for cid in cell_ids:
        r = db.execute(
            select(ExposureMetric).where(ExposureMetric.cell_id == cid)
            .order_by(desc(ExposureMetric.observed_at)).limit(1)
        ).scalar_one_or_none()
        if r:
            metrics.append(r)
    return {
        "total_teu": sum(x.teu for x in metrics),
        "total_vulnerable_teu": sum(x.vulnerable_teu for x in metrics),
        "population_exposed": sum(x.population_exposed for x in metrics),
        "vulnerable_population_exposed": sum(x.vulnerable_population_exposed for x in metrics),
        "mean_confidence": (sum(x.confidence for x in metrics)/len(metrics)) if metrics else 0,
    }

def _thermal_summary(db: Session, area_id: str):
    hotspots = db.execute(
        select(ThermalHotspot).where(ThermalHotspot.area_id == area_id)
        .order_by(desc(ThermalHotspot.detected_at))
    ).scalars().all()
    latest = hotspots[0] if hotspots else None
    return {
        "hotspot_count": len(hotspots),
        "peak_temperature_c": latest.peak_temperature_c if latest else None,
        "confidence": latest.confidence if latest else 0,
    }

def _attribution(db: Session, area_id: str):
    cell_ids = db.execute(select(ThermalCell.id).where(ThermalCell.area_id == area_id)).scalars().all()
    out=[]
    for cid in cell_ids:
        r=db.execute(
            select(DriverAttribution).where(DriverAttribution.cell_id==cid)
            .order_by(desc(DriverAttribution.observed_at)).limit(1)
        ).scalar_one_or_none()
        if r:
            out.append({"cell_id":cid,"dominant_driver":r.dominant_driver,"confidence":r.confidence})
    return out

def _optimizer_summary(db: Session, run: OptimizationRun):
    result = None
    if run.scenario_id:
        result=db.execute(select(ScenarioResult).where(ScenarioResult.scenario_id==run.scenario_id)).scalar_one_or_none()
    selections=db.execute(select(OptimizationSelection).where(OptimizationSelection.run_id==run.id)).scalars().all()
    return {
        "objective": run.objective,
        "budget": run.budget,
        "total_cost": run.total_cost or 0,
        "selected_count": run.selected_count or 0,
        "confidence": result.confidence if result else 0,
        "teu_reduction": result.teu_reduction if result else 0,
        "teu_reduction_pct": result.teu_reduction_pct if result else 0,
        "vulnerable_teu_reduction": result.vulnerable_teu_reduction if result else 0,
        "actions": [{
            "cell_id":s.cell_id,
            "intervention_id":s.intervention_id,
            "cost":s.cost,
            "estimated_teu_benefit":s.estimated_teu_benefit,
            "estimated_vulnerable_teu_benefit":s.estimated_vulnerable_teu_benefit,
            "confidence":s.confidence,
        } for s in selections],
    }

def run_agents(db: Session, req: AgentDecisionRequest):
    optimization = _latest_optimizer(db, req.area_id, req.optimization_run_id)
    if optimization is None:
        raise ValueError("no completed optimization run found")

    run=AgentRun(
        area_id=req.area_id,
        optimization_run_id=optimization.id,
        status="running",
        mode=req.mode,
        request_json=req.model_dump(),
        summary_json={},
        confidence=0,
    )
    db.add(run); db.commit(); db.refresh(run)

    area_exp=_area_exposure(db, req.area_id)
    thermal=_thermal_summary(db, req.area_id)
    attribution=_attribution(db, req.area_id)
    optimizer=_optimizer_summary(db, optimization)

    cell_ids=db.execute(select(ThermalCell.id).where(ThermalCell.area_id==req.area_id)).scalars().all()
    truth_categories=set()
    evidence=[]

    observations=[]
    for cid in cell_ids:
        obs=db.execute(
            select(ThermalObservation).where(ThermalObservation.cell_id==cid)
            .order_by(desc(ThermalObservation.observed_at)).limit(1)
        ).scalar_one_or_none()
        if obs:
            observations.append(obs)
            truth_categories.add(obs.source_type)
            evidence.append({
                "claim_key":f"thermal:{cid}",
                "source_type":"thermal_observation",
                "source_ref":obs.id,
                "truth_category":obs.source_type,
                "confidence":0.95 if obs.source_type in {"provider","observed"} else 0.80 if obs.source_type=="fixture" else 0.70,
                "evidence":{"temperature_c":obs.temperature_c,"observed_at":obs.observed_at.isoformat()},
            })

    contexts=db.execute(select(UrbanContextCell).where(UrbanContextCell.cell_id.in_(cell_ids))).scalars().all()
    for ctx in contexts:
        cat=ctx.source_json.get("truth_category","unknown")
        truth_categories.add(cat)
        evidence.append({
            "claim_key":f"context:{ctx.cell_id}",
            "source_type":"urban_context",
            "source_ref":ctx.id,
            "truth_category":cat,
            "confidence":ctx.data_quality,
            "evidence":{"population":ctx.population,"vulnerability_index":ctx.vulnerability_index},
        })

    for e in evidence:
        db.add(EvidenceRecord(run_id=run.id, claim_key=e["claim_key"], source_type=e["source_type"], source_ref=e["source_ref"], truth_category=e["truth_category"], confidence=e["confidence"], evidence_json=e["evidence"]))
    db.commit()

    findings=[
        scout_agent(area_exp, thermal),
        diagnostician_agent(attribution),
        exposure_agent(area_exp),
        planner_agent(optimizer),
        skeptic_agent(optimizer=optimizer, source_truth_categories=truth_categories, mode=req.mode),
        evidence_agent(evidence),
    ]
    executive=executive_agent(findings, req.min_recommendation_confidence)
    findings.append(executive)

    for f in findings:
        db.add(AgentFinding(
            run_id=run.id,
            agent_name=f["agent"],
            finding_type=f["finding_type"],
            severity=f["severity"],
            confidence=f["confidence"],
            content_json=f["content"],
        ))

    rec=Recommendation(
        run_id=run.id,
        headline=executive["content"]["headline"],
        decision_status=executive["content"]["decision_status"],
        confidence=executive["confidence"],
        requires_human_review=executive["content"]["requires_human_review"],
        recommended_actions_json={"actions":executive["content"]["recommended_actions"]},
        skeptic_findings_json=next(x["content"] for x in findings if x["agent"]=="Skeptic"),
        evidence_summary_json=next(x["content"] for x in findings if x["agent"]=="Evidence"),
        executive_summary_json={
            "mode":req.mode,
            "optimizer_run_id":optimization.id,
            "objective":optimization.objective,
            "budget":optimization.budget,
            "total_cost":optimization.total_cost,
            "teu_reduction":optimizer["teu_reduction"],
            "teu_reduction_pct":optimizer["teu_reduction_pct"],
        },
    )
    db.add(rec)

    run.status="complete"
    run.requires_human_review=rec.requires_human_review
    run.confidence=rec.confidence
    run.summary_json={
        "decision_status":rec.decision_status,
        "agents":[f["agent"] for f in findings],
        "truth_categories":sorted(truth_categories),
    }
    run.completed_at=datetime.now(timezone.utc)
    db.commit(); db.refresh(run); db.refresh(rec)
    return run, rec
