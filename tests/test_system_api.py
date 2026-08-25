from fastapi.testclient import TestClient
from app.main import app


def test_system_capabilities_route():
    client = TestClient(app)

    r = client.get("/api/v1/system/capabilities")

    assert r.status_code == 200, r.text

    body = r.json()

    assert body["engines"]["gemma4"] is True
    assert body["engines"]["thermalway"] is True
    assert body["engines"]["provider_operations"] is True
    assert body["engines"]["portfolio_optimizer"] is True
    assert "command" in body["modes"]
    assert "investment" in body["modes"]


def test_system_status_route():
    client = TestClient(app)

    r = client.get("/api/v1/system/status")

    assert r.status_code == 200, r.text

    body = r.json()

    assert body["service"] == "HELIOS"
    assert body["intelligence"]["firewall"] == "enabled"
    assert body["truth_policy"]["prediction_claims"] is False
    assert body["truth_policy"]["modelled_is_causal"] is False
    assert body["truth_policy"]["human_review_gate"] is True


def test_provider_native_optimizer_route_is_registered():
    paths = set(TestClient(app).get("/openapi.json").json()["paths"])
    assert "/api/v1/optimizer/provider-native/latest" in paths
