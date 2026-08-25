import json
from app.db.session import SessionLocal
from app.decision_science.service import run_decision_science
from app.thermalway.network_audit import audit_real_network
db=SessionLocal()
try:
    ds=run_decision_science(db)
    tw=audit_real_network(db)
    print(json.dumps({
      "decision_science":{
        "id":ds.id,"status":ds.status,"robustness_score":ds.robustness_score,
        "max_regret":ds.max_regret,"mean_regret":ds.mean_regret,
        "voi_top":ds.voi_json["top_information_priorities"][:3],
        "budget_frontier":ds.reverse_optimization_json["budget_frontier"],
        "sequence":ds.sequencing_json,
        "what_changes_mind":ds.what_changes_mind_json,
      },
      "thermalway_network_audit":{
        "id":tw.id,"status":tw.status,"real_osm_network_proven":tw.real_osm_network_proven,
        "source_table":tw.source_table,"geometry_column":tw.geometry_column,
        "line_feature_count":tw.line_feature_count,"candidate_tables":tw.candidate_tables_json
      }
    },indent=2,default=str))
    print("PASS: advanced decision science stored")
    print("THERMALWAY_NETWORK_STATUS:",tw.status)
finally:db.close()
