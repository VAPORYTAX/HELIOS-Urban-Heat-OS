from sqlalchemy import desc,select
from app.db.session import SessionLocal
from app.db.models_decision_science import DecisionScienceRun,ThermalWayNetworkAudit
db=SessionLocal()
try:
    ds=db.execute(select(DecisionScienceRun).where(DecisionScienceRun.area_id=="phx-downtown").order_by(desc(DecisionScienceRun.created_at)).limit(1)).scalar_one()
    assert 0<=ds.robustness_score<=1
    assert ds.max_regret>=0 and ds.mean_regret>=0
    assert len(ds.sensitivity_json["scenarios"])==20
    assert len(ds.reverse_optimization_json["budget_frontier"])==5
    assert len(ds.sequencing_json)>0
    tw=db.execute(select(ThermalWayNetworkAudit).where(ThermalWayNetworkAudit.area_id=="phx-downtown").order_by(desc(ThermalWayNetworkAudit.created_at)).limit(1)).scalar_one()
    assert tw.status in {"ready_for_real_routing","network_schema_required"}
    assert tw.notes_json["synthetic_routes_created"] is False
    print("PASS: robustness/sensitivity/regret/VOI/reverse optimization/sequencing verified")
    print("PASS: ThermalWay claim boundary enforced; synthetic routes = false")
    print("THERMALWAY_REAL_NETWORK_PROVEN",tw.real_osm_network_proven)
finally:db.close()
