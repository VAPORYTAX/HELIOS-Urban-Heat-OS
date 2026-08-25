from types import SimpleNamespace
from app.interventions.catalog import INTERVENTIONS
from app.interventions.engine import suitability, estimate_cost

def context(**kw):
    base = dict(
        road_fraction=0.4,
        shade_fraction=0.1,
        vegetation_fraction=0.1,
        solar_exposure_index=0.9,
        building_fraction=0.35,
        impervious_fraction=0.8,
        vulnerability_index=0.7,
        data_quality=0.9,
    )
    base.update(kw)
    return SimpleNamespace(**base)

def driver(name="low_vegetation"):
    return SimpleNamespace(dominant_driver=name)

def test_shade_structure_is_feasible_for_exposed_cell():
    item = next(x for x in INTERVENTIONS if x["id"] == "shade_structure")
    out = suitability(item, context(), driver("solar_exposure"))
    assert out["feasible"] is True
    assert out["suitability_score"] > 0.7

def test_cool_roof_rejects_low_building_fraction():
    item = next(x for x in INTERVENTIONS if x["id"] == "cool_roof")
    out = suitability(item, context(building_fraction=0.05), driver("built_form"))
    assert out["feasible"] is False

def test_estimated_cost_positive():
    item = next(x for x in INTERVENTIONS if x["id"] == "tree_canopy")
    assert estimate_cost(item, 0.8) > 0
