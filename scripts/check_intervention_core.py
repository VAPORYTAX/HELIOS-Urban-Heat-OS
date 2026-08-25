import json, urllib.request

BASE="http://127.0.0.1:8080/api/v1"

def get(path):
    with urllib.request.urlopen(BASE+path, timeout=10) as r:
        return json.load(r)

catalog = get("/interventions/catalog")
candidates = get("/interventions/candidates?area_id=phx-downtown")
scenarios = get("/scenarios?area_id=phx-downtown")

assert len(catalog) == 5, len(catalog)
assert len(candidates) >= 20, len(candidates)
assert scenarios, "no scenarios found"

scenario_id = scenarios[0]["id"]
result = get(f"/scenarios/{scenario_id}/result")

assert result["projected_teu"] <= result["baseline_teu"]
assert result["teu_reduction"] >= 0
assert result["total_cost"] <= 120000 + 1e-6
assert 0 <= result["confidence"] <= 1
assert result["uncertainty_interval"][0] <= result["teu_reduction"] <= result["uncertainty_interval"][1]

print(json.dumps({
    "catalog": len(catalog),
    "candidates": len(candidates),
    "latest_scenario": scenarios[0],
    "result": {
        "baseline_teu": result["baseline_teu"],
        "projected_teu": result["projected_teu"],
        "teu_reduction": result["teu_reduction"],
        "teu_reduction_pct": result["teu_reduction_pct"],
        "total_cost": result["total_cost"],
        "thermal_roi": result["thermal_roi"],
        "confidence": result["confidence"],
        "uncertainty_interval": result["uncertainty_interval"],
    }
}, indent=2))
print("PASS: HELIOS intervention and counterfactual core is healthy")
