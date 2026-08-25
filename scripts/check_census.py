import json, urllib.request

BASE = "http://127.0.0.1:8080/api/v1"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)

ready = get("/demographics/readiness")
cells = get("/demographics/cells?area_id=phx-downtown")
context = get("/context/cells?area_id=phx-downtown")
data_ready = get("/data/readiness")

assert ready["configured"] is True, ready
assert len(cells) == 4, cells
assert all(x["population"] >= 0 for x in cells)
assert all(0 <= x["vulnerability_index"] <= 1 for x in cells)
assert all(x["source"]["population_source"].startswith("US Census ACS 2024") for x in cells)
assert all(x["source"].get("truth_category") == "derived" for x in cells)
assert all(x["source"].get("truth_category") == "mixed" for x in context)
assert data_ready["fortyguard"]["configured"] is False

print(json.dumps({
    "census": ready,
    "cells": [{
        "cell_id": x["cell_id"],
        "population": round(x["population"], 2),
        "population_density_km2": round(x["population_density_km2"], 2),
        "under5_population": round(x["under5_population"], 2),
        "age65_population": round(x["age65_population"], 2),
        "poverty_population": round(x["poverty_population"], 2),
        "no_vehicle_households": round(x["no_vehicle_households"], 2),
        "vulnerability_index": round(x["vulnerability_index"], 4),
        "confidence": round(x["confidence"], 4),
    } for x in cells],
    "fortyguard_configured": data_ready["fortyguard"]["configured"],
}, indent=2))
print("PASS: HELIOS Census demographics adapter is healthy")
