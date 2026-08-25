from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import desc,select
from sqlalchemy.orm import Session
from app.contextforge.contracts import ContextBuildRequest
from app.contextforge.service import build_context_packet
from app.db.models_context import ContextPacket,PromptRegistry
from app.db.session import get_db
router=APIRouter(prefix="/context",tags=["contextforge"])
@router.post("/build")
def build(body:ContextBuildRequest,db:Session=Depends(get_db)):
    try:r=build_context_packet(db,body)
    except ValueError as exc:raise HTTPException(404,detail=str(exc)) from exc
    return {"id":r.id,"area_id":r.area_id,"task_type":r.task_type,"mode":r.mode,"context_hash":r.context_hash,
            "prompt_bundle_version":r.prompt_bundle_version,"token_budget":r.token_budget,
            "estimated_tokens":r.estimated_tokens,"status":r.status,"packet":r.packet_json}
@router.get("/packets")
def packets(area_id:str,db:Session=Depends(get_db)):
    rows=db.execute(select(ContextPacket).where(ContextPacket.area_id==area_id).order_by(desc(ContextPacket.created_at))).scalars().all()
    return [{"id":r.id,"task_type":r.task_type,"mode":r.mode,"context_hash":r.context_hash,
             "prompt_bundle_version":r.prompt_bundle_version,"token_budget":r.token_budget,
             "estimated_tokens":r.estimated_tokens,"status":r.status,"created_at":r.created_at} for r in rows]
@router.get("/packets/{packet_id}")
def packet(packet_id:str,db:Session=Depends(get_db)):
    r=db.get(ContextPacket,packet_id)
    if r is None:raise HTTPException(404,detail="context packet not found")
    return {"id":r.id,"area_id":r.area_id,"task_type":r.task_type,"mode":r.mode,"user_intent":r.user_intent,
            "context_hash":r.context_hash,"prompt_bundle_version":r.prompt_bundle_version,
            "token_budget":r.token_budget,"estimated_tokens":r.estimated_tokens,"status":r.status,
            "packet":r.packet_json,"evidence":r.evidence_json,"created_at":r.created_at}
@router.get("/prompts")
def prompts(db:Session=Depends(get_db)):
    rows=db.execute(select(PromptRegistry).order_by(PromptRegistry.id)).scalars().all()
    return [{"id":r.id,"name":r.name,"version":r.version,"role":r.role,"active":r.active,"metadata":r.metadata_json} for r in rows]
