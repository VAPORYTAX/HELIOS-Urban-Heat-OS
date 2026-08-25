from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.agents.contracts import AgentDecisionRequest
from app.agents.service import run_agents
from app.db.models_agents import AgentFinding, AgentRun, EvidenceRecord, Recommendation
from app.db.session import get_db

router=APIRouter(prefix="/agents",tags=["agents"])

@router.post("/run")
def run(body:AgentDecisionRequest,db:Session=Depends(get_db)):
    try:
        agent_run,rec=run_agents(db,body)
    except ValueError as exc:
        raise HTTPException(404,detail=str(exc)) from exc
    return {
        "run_id":agent_run.id,
        "status":agent_run.status,
        "mode":agent_run.mode,
        "decision_status":rec.decision_status,
        "headline":rec.headline,
        "confidence":rec.confidence,
        "requires_human_review":rec.requires_human_review,
    }

@router.get("/runs")
def runs(area_id:str,db:Session=Depends(get_db)):
    rows=db.execute(
        select(AgentRun).where(AgentRun.area_id==area_id).order_by(desc(AgentRun.created_at))
    ).scalars().all()
    return [{
        "id":r.id,"optimization_run_id":r.optimization_run_id,"status":r.status,
        "mode":r.mode,"confidence":r.confidence,"requires_human_review":r.requires_human_review,
        "summary":r.summary_json,"created_at":r.created_at
    } for r in rows]

@router.get("/runs/{run_id}")
def run_detail(run_id:str,db:Session=Depends(get_db)):
    run=db.get(AgentRun,run_id)
    if not run:
        raise HTTPException(404,detail="agent run not found")
    findings=db.execute(select(AgentFinding).where(AgentFinding.run_id==run_id)).scalars().all()
    evidence=db.execute(select(EvidenceRecord).where(EvidenceRecord.run_id==run_id)).scalars().all()
    rec=db.execute(select(Recommendation).where(Recommendation.run_id==run_id)).scalar_one_or_none()
    return {
        "id":run.id,
        "area_id":run.area_id,
        "optimization_run_id":run.optimization_run_id,
        "status":run.status,
        "mode":run.mode,
        "confidence":run.confidence,
        "requires_human_review":run.requires_human_review,
        "summary":run.summary_json,
        "findings":[{
            "agent":f.agent_name,"type":f.finding_type,"severity":f.severity,
            "confidence":f.confidence,"content":f.content_json
        } for f in findings],
        "evidence":[{
            "claim_key":e.claim_key,"source_type":e.source_type,"source_ref":e.source_ref,
            "truth_category":e.truth_category,"confidence":e.confidence,"evidence":e.evidence_json
        } for e in evidence],
        "recommendation":None if not rec else {
            "headline":rec.headline,
            "decision_status":rec.decision_status,
            "confidence":rec.confidence,
            "requires_human_review":rec.requires_human_review,
            "recommended_actions":rec.recommended_actions_json,
            "skeptic_findings":rec.skeptic_findings_json,
            "evidence_summary":rec.evidence_summary_json,
            "executive_summary":rec.executive_summary_json,
        }
    }

@router.get("/recommendations/latest")
def latest(area_id:str,db:Session=Depends(get_db)):
    run=db.execute(
        select(AgentRun).where(AgentRun.area_id==area_id,AgentRun.status=="complete")
        .order_by(desc(AgentRun.created_at)).limit(1)
    ).scalar_one_or_none()
    if not run:
        raise HTTPException(404,detail="no recommendation")
    rec=db.execute(select(Recommendation).where(Recommendation.run_id==run.id)).scalar_one()
    return {
        "run_id":run.id,
        "headline":rec.headline,
        "decision_status":rec.decision_status,
        "confidence":rec.confidence,
        "requires_human_review":rec.requires_human_review,
        "recommended_actions":rec.recommended_actions_json,
        "skeptic_findings":rec.skeptic_findings_json,
        "evidence_summary":rec.evidence_summary_json,
        "executive_summary":rec.executive_summary_json,
    }
