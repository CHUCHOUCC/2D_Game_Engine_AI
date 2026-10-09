import time

from fastapi.testclient import TestClient

from app.main import app
from app.security import ReplayCache
from tests.tokens import KEY, auth


def client(monkeypatch, key=KEY):
    monkeypatch.setenv("AI_SERVICE_KEY", key)
    return TestClient(app)


def test_valid_token_is_accepted(monkeypatch):
    assert client(monkeypatch).get("/info", headers=auth()).status_code == 200
