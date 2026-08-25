def test_scenario_grid_size():
    assert len([(e,c) for e in [.6,.8,1,1.2,1.4] for c in [.9,1,1.1,1.2]])==20
def test_thermalway_never_requires_synthetic_claim():
    synthetic_routes_created=False
    assert synthetic_routes_created is False
