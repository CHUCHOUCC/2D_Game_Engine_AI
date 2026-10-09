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



def test_missing_or_garbage_token_is_rejected(monkeypatch):
    c = client(monkeypatch)
    assert c.get("/info").status_code == 401
    assert c.get("/info", headers={"Authorization": "Bearer nonsense"}).status_code == 401



def test_the_raw_key_header_is_not_enough(monkeypatch):
    assert client(monkeypatch).get("/info", headers={"X-Service-Key": KEY}).status_code == 401



def test_wrong_key_audience_issuer_or_expired_token_is_rejected(monkeypatch):
    c = client(monkeypatch)
    for headers in (
        auth(key="another-key-that-is-also-32-chars-long"),
        auth(audience="billing"),
        auth(issuer="someone-else"),
        auth(lifetime=-120),
    ):
        assert c.get("/info", headers=headers).status_code == 401



def test_a_token_cannot_be_used_twice(monkeypatch):
    c = client(monkeypatch)
    headers = auth(jti="replay-me")
    assert c.get("/info", headers=headers).status_code == 200
    response = c.get("/info", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Service token already used"
