from app.provider_decision.service import CATALOG
def test_catalog_has_core_interventions():
    assert {"shade_structure","tree_canopy","cool_roof","cool_pavement","cooling_center"}.issubset(CATALOG)
def test_assumed_cooling_nonnegative():
    assert all(v["delta_c"]>=0 for v in CATALOG.values())
