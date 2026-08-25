from app.realdata.osm import build_query, classify_facility, parse_elements, road_width_m

def test_query_contains_geometry_output():
    q = build_query(33.4, -112.1, 33.5, -112.0)
    assert "out geom;" in q
    assert '["building"]' in q
    assert '["highway"]' in q

def test_parse_node():
    payload = {"elements": [{
        "type": "node", "id": 1, "lat": 33.45, "lon": -112.07,
        "tags": {"amenity": "school", "name": "X"}
    }]}
    rows = parse_elements(payload)
    assert len(rows) == 1
    assert rows[0].geometry.geom_type == "Point"

def test_facility_mapping():
    assert classify_facility({"amenity": "school"})[0] == "school"
    assert classify_facility({"amenity": "hospital"})[0] == "healthcare"
    assert classify_facility({"highway": "bus_stop"})[0] == "transit"

def test_road_width():
    assert road_width_m({"highway": "primary"}) > road_width_m({"highway": "footway"})
