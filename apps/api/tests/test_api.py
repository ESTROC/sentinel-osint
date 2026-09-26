from fastapi.testclient import TestClient
from main import app, get_repo
from app.repository import MemoryRepository


def fresh_repo():
    return MemoryRepository()


app.dependency_overrides[get_repo] = fresh_repo
client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_events_and_metrics():
    events = client.get("/api/events")
    metrics = client.get("/api/metrics")
    assert events.status_code == 200
    assert len(events.json()) >= 5
    assert metrics.json()["total_events"] >= 5


def test_event_detail_and_brief():
    event_id = client.get("/api/events").json()[0]["id"]
    assert client.get(f"/api/events/{event_id}").status_code == 200
    brief = client.get(f"/api/events/{event_id}/brief")
    assert brief.status_code == 200
    assert "known_facts" in brief.json()


def test_demo_write_flow():
    event_id = "demo-001"
    response = client.patch(f"/api/events/{event_id}", json={"status": "MONITORING", "verified": True, "actor": "test-analyst"})
    assert response.status_code == 200
    assert response.json()["status"] == "MONITORING"
