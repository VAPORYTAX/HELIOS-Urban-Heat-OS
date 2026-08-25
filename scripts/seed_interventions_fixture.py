import json
from app.db.session import SessionLocal
from app.interventions.service import build_fixture_scenario, generate_candidates, seed_catalog, simulate_scenario

db = SessionLocal()
try:
    seed_catalog(db)
    candidates = generate_candidates(db, "phx-downtown")
    scenario = build_fixture_scenario(db, "phx-downtown")
    result = simulate_scenario(db, scenario.id)
    print(json.dumps({
        "catalog_count": 5,
        "candidate_count": len(candidates),
        "scenario_id": scenario.id,
        "baseline_teu": result.baseline_teu,
        "projected_teu": result.projected_teu,
        "teu_reduction": result.teu_reduction,
        "teu_reduction_pct": result.teu_reduction_pct,
        "total_cost": result.total_cost,
        "thermal_roi": result.thermal_roi,
        "confidence": result.confidence,
        "uncertainty_interval": [result.lower_teu_reduction, result.upper_teu_reduction],
    }, indent=2))
finally:
    db.close()
