from app.thermal.fixture import fixture_grid,fixture_observations
def test_grid(): assert len(fixture_grid())==4 and len({x['id'] for x in fixture_grid()})==4
def test_deterministic(): assert fixture_observations(3)==fixture_observations(3)
