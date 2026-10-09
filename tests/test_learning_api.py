from fastapi.testclient import TestClient

from app.main import app
from tests.tokens import KEY, auth

WIN = {"outcome": "won", "score": 150, "coins_collected": 3, "coins_total": 3, "enemies_defeated": 0,
       "damage_taken": 0, "deaths": 0, "duration_ms": 25000}


def client(monkeypatch):
    monkeypatch.setenv("AI_SERVICE_KEY", KEY)
    return TestClient(app)


def test_learn_starts_from_an_empty_model(monkeypatch):
    body = client(monkeypatch).post("/learn", json={"model": {}, "run": WIN}, headers=auth()).json()
    assert body["model"]["runs"] == 1
    assert body["difficulty"] > 0.5
    assert 0 <= body["reward"] <= 1
    assert body["obstacle_budget"] >= 12



def test_learn_continues_from_the_given_model(monkeypatch):
    c = client(monkeypatch)
    first = c.post("/learn", json={"model": {}, "run": WIN}, headers=auth()).json()["model"]
    second = c.post("/learn", json={"model": first, "run": WIN}, headers=auth()).json()["model"]
    assert second["runs"] == 2
    assert second["difficulty"] > first["difficulty"]



def test_learn_rejects_invalid_runs(monkeypatch):
    c = client(monkeypatch)
    assert c.post("/learn", json={"run": {**WIN, "outcome": "draw"}}, headers=auth()).status_code == 422
    assert c.post("/learn", json={"model": {}}, headers=auth()).status_code == 422



def test_obstacles_endpoint(monkeypatch):
    scene = [{"id": "hero", "kind": "player", "x": 64, "y": 480},
             {"id": "c1", "kind": "coin", "x": 800, "y": 480}]
    response = client(monkeypatch).post("/obstacles", json={"model": {}, "scene": scene, "count": 6}, headers=auth())
    assert response.status_code == 200
    body = response.json()
    assert len(body["objects"]) == 6
    assert body["difficulty"] == 0.5
    assert 0 < body["open_area"] <= 1
