from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import desc,select
from sqlalchemy.orm import Session
from app.db.models_fortyguard import FortyGuardIngestRun
from app.db.session import get_db
from app.fortyguard_live.service import ingest_live_hour
router=APIRouter(prefix="/fortyguard",tags=["fortyguard-live"])
@router.post("/ingest/current")
def ingest(area_id:str="phx-downtown",db:Session=Depends(get_db)):
    try:r=ingest_live_hour(db,area_id)
    except Exception as exc: raise HTTPException(502,detail=str(exc)) from exc
    return {"id":r.id,"activity_id":r.activity_id,"status":r.status,"target_time":r.target_time,
            "tile_count":r.tile_count,"cells_updated":r.cells_updated,"stats":r.stats_json,"mapping":r.mapping_json}
@router.get("/ingest/runs")
def runs(area_id:str,db:Session=Depends(get_db)):
    rows=db.execute(select(FortyGuardIngestRun).where(FortyGuardIngestRun.area_id==area_id).order_by(desc(FortyGuardIngestRun.created_at))).scalars().all()
    return [{"id":r.id,"activity_id":r.activity_id,"status":r.status,"target_time":r.target_time,
             "tile_count":r.tile_count,"cells_updated":r.cells_updated,"created_at":r.created_at} for r in rows]
