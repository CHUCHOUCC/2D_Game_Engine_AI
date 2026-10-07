from fastapi.testclient import TestClient

from app.agent import GameAgent
from app.main import app, get_agent
from app.providers import AiProvider, AiProviderError, SimulatedProvider


class FailingProvider(AiProvider):
    def complete(self, system, user):
        raise AiProviderError("down")


def client_with(provider, monkeypatch, key="s3cret"):
    monkeypatch.setenv("AI_SERVICE_KEY", key)
    app.dependency_overrides[get_agent] = lambda: GameAgent(provider)
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_health_needs_no_key():
    assert TestClient(app).get("/health").json() == {"ok": True}


def test_generate_without_key_is_rejected(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    assert client.post("/generate", json={"prompt": "a coin"}).status_code == 401


def test_generate_with_wrong_key_is_rejected(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    response = client.post("/generate", json={"prompt": "a coin"}, headers={"X-Service-Key": "wrong"})
    assert response.status_code == 401


def test_generate_is_unavailable_when_no_key_is_configured(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch, key="")
    response = client.post("/generate", json={"prompt": "a coin"}, headers={"X-Service-Key": ""})
    assert response.status_code == 503


def test_generate_with_the_right_key_returns_objects(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    response = client.post("/generate", json={"prompt": "an enemy at 50 60"}, headers={"X-Service-Key": "s3cret"})
    assert response.status_code == 200
    assert response.json() == {"objects": [{"id": "enemy-1", "kind": "enemy", "x": 50.0, "y": 60.0}]}


def test_provider_failure_returns_502(monkeypatch):
    client = client_with(FailingProvider(), monkeypatch)
    response = client.post("/generate", json={"prompt": "a coin"}, headers={"X-Service-Key": "s3cret"})
    assert response.status_code == 502


def test_empty_prompt_is_rejected(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    response = client.post("/generate", json={"prompt": ""}, headers={"X-Service-Key": "s3cret"})
    assert response.status_code == 422


def test_service_does_not_enable_cors(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    response = client.options(
        "/generate",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in response.headers
