from fastapi.testclient import TestClient
from app.main import app

def test_root():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["name"] == "HELIOS"

def test_provider_health_does_not_expose_secret():
    client = TestClient(app)
    r = client.get("/api/v1/provider/fortyguard/health")
    assert r.status_code == 200
    text = r.text.lower()
    assert "api-key" not in text
