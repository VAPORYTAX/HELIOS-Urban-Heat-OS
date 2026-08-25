from app.thermalway.osm_ingest import _walkable
def test_motorway_rejected():
    assert not _walkable({"highway":"motorway"})
def test_private_rejected():
    assert not _walkable({"highway":"footway","access":"private"})
def test_footway_allowed():
    assert _walkable({"highway":"footway"})
