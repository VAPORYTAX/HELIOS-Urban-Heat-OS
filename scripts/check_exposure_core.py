import json
import urllib.request

BASE = "http://127.0.0.1:8080/api/v1"

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.load(r)

area = get("/exposure/area?area_id=phx-downtown")
cells = get("/exposure/cells?area_id=phx-downtown")
attrib = get("/attribution/area?area_id=phx-downtown")
context = get("/context/cells?area_id=phx-downtown")
facilities = get("/facilities?area_id=phx-downtown")

assert area["cell_count"] == 4, area
assert len(cells) == 4, cells
assert len(attrib) == 4, attrib
assert len(context) == 4, context
assert len(facilities) == 3, facilities
assert area["total_teu"] > 0
assert area["total_vulnerable_teu"] > 0

drivers = {}
for row in attrib:
    drivers[row["dominant_driver"]] = drivers.get(row["dominant_driver"], 0) + 1

print(json.dumps({
    "area_id": area["area_id"],
    "total_teu": area["total_teu"],
    "total_vulnerable_teu": area["total_vulnerable_teu"],
    "population_exposed": area["population_exposed"],
    "vulnerable_population_exposed": area["vulnerable_population_exposed"],
    "mean_confidence": area["mean_confidence"],
    "cells": len(cells),
    "facilities": len(facilities),
    "dominant_driver_counts": drivers,
    "highest_teu_cell": max(cells, key=lambda x: x["teu"]),
}, indent=2))

print("PASS: HELIOS exposure, vulnerability, TEU and attribution core is healthy")
