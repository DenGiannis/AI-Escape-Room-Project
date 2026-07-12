"""
Smoke tests for the FastAPI endpoints that don't call OpenAI - all offline.
"""

from fastapi.testclient import TestClient

def test_start_game_creates_a_session(client: TestClient):
    resp = client.post("/api/v1/game/start", json={"player_name": "Ada"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["player_name"] == "Ada"
    assert data["current_room"] == "entrance_hall"
    assert data["inventory"] == []
    assert data["is_escaped"] is False
    assert data["session_id"]          # a non-empty id was assigned
    assert "Athena" in data["message"]  # the welcome text is included


def test_summary_reflects_a_started_game(client: TestClient):
    start = client.post("/api/v1/game/start", json={"player_name": "Grace"}).json()
    session_id = start["session_id"]

    resp = client.get(f"/api/v1/game/summary/{session_id}")
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["player_name"] == "Grace"
    assert summary["current_room"] == "entrance_hall"
    assert summary["hint_count"] == 0


def test_inventory_starts_empty(client: TestClient):
    start = client.post("/api/v1/game/start", json={"player_name": "Alan"}).json()
    resp = client.get(f"/api/v1/game/inventory/{start['session_id']}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["inventory"] == []
    assert body["found_items"] == []


def test_summary_for_unknown_session_returns_404(client: TestClient):
    resp = client.get("/api/v1/game/summary/does-not-exist")
    assert resp.status_code == 404
