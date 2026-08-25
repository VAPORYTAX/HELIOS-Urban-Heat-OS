import json, urllib.request

BASE = "http://127.0.0.1:8080/api/v1"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)

ready = get("/data/readiness")
runs = get("/data/sync/runs?area_id=phx-downtown")
context = get("/context/cells?area_id=phx-downtown")
facilities = get("/facilities?area_id=phx-downtown")

assert ready["openstreetmap"]["configured"] is True
assert runs and runs[0]["provider"] == "openstreetmap_overpass"
assert runs[0]["status"] == "complete"
assert len(context) == 4
assert all(x["source"].get("truth_category") == "mixed" for x in context)
assert all(x["metadata"].get("truth_category") == "observed" for x in facilities)

print(json.dumps({
    "provider_readiness": ready,
    "latest_sync": runs[0],
    "urban_context_cells": len(context),
    "real_osm_facilities": len(facilities),
    "context_truth_categories": sorted(set(x["source"].get("truth_category") for x in context)),
}, indent=2))
print("PASS: HELIOS real-data integration layer is healthy")
