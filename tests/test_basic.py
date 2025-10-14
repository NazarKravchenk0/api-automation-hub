import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200

def test_form_webhook_creates_lead():
    payload = {"name": "Test User", "email": "test@example.com", "phone": "+1 202-555-0142", "source": "landing"}
    r = client.post("/webhooks/form", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "test@example.com"
