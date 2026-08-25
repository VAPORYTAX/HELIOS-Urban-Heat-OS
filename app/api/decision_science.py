from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models_decision_science import DecisionScienceRun
from app.db.session import get_db

router = APIRouter(prefix="/decision-science", tags=["decision-science"])


def serialize(r: DecisionScienceRun):
    return {
        "id": r.id,
        "area_id": r.area_id,
        "optimizer_run_id": r.optimizer_run_id,
        "status": r.status,
        "robustness_score": r.robustness_score,
        "max_regret": r.max_regret,
        "mean_regret": r.mean_regret,
        "sensitivity": r.sensitivity_json,
        "value_of_information": r.voi_json,
        "reverse_optimization": r.reverse_optimization_json,
        "sequencing": r.sequencing_json,
        "what_changes_mind": r.what_changes_mind_json,
        "truth_category": "modelled_decision_science",
        "requires_human_review": True,
        "created_at": r.created_at,
    }


@router.get("/latest")
def latest(area_id: str = "phx-downtown", db: Session = Depends(get_db)):
    row = db.execute(
        select(DecisionScienceRun)
        .where(DecisionScienceRun.area_id == area_id)
        .order_by(desc(DecisionScienceRun.created_at))
        .limit(1)
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(404, detail="decision science run not found")
    return serialize(row)
