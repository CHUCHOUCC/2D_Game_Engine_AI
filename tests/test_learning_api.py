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
