import json
import urllib.request

BASE = "http://127.0.0.1:8080/api/v1"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)

runs = get("/optimizer/runs?area_id=phx-downtown")
assert runs, "no optimization runs"
latest = runs[0]
detail = get(f"/optimizer/runs/{latest['id']}")

assert detail["status"] == "complete", detail
assert detail["selected_count"] > 0, detail
assert detail["total_cost"] <= detail["budget"] + 1e-6, detail
assert detail["scenario_result"]["teu_reduction"] > 0, detail
assert 0 <= detail["scenario_result"]["confidence"] <= 1

print(json.dumps({
    "latest_run": {
        "id": detail["id"],
        "objective": detail["objective"],
        "solver_status": detail["solver_status"],
        "budget": detail["budget"],
        "total_cost": detail["total_cost"],
        "selected_count": detail["selected_count"],
        "teu_reduction": detail["scenario_result"]["teu_reduction"],
        "teu_reduction_pct": detail["scenario_result"]["teu_reduction_pct"],
        "vulnerable_teu_reduction": detail["scenario_result"]["vulnerable_teu_reduction"],
        "thermal_roi": detail["scenario_result"]["thermal_roi"],
        "confidence": detail["scenario_result"]["confidence"],
    },
    "selected_actions": [
        {
            "cell_id": s["cell_id"],
            "intervention_id": s["intervention_id"],
            "cost": s["cost"],
            "estimated_teu_benefit": s["estimated_teu_benefit"],
            "confidence": s["confidence"],
        }
        for s in detail["selections"]
    ],
}, indent=2))
print("PASS: HELIOS mathematical portfolio optimizer is healthy")
