from app.realdata.census import status

def test_census_status_explicitly_requires_key():
    s = status()
    assert s["requires_api_key"] is True
    assert s["truth_category"] == "observed"
