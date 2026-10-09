from fastapi.testclient import TestClient

from app.agent import GameAgent
from app.main import app, get_agent
from app.providers import AiProvider, AiProviderError, SimulatedProvider
from tests.tokens import KEY, auth


class FailingProvider(AiProvider):
    def complete(self, system, user):
        raise AiProviderError("down")


def client_with(provider, monkeypatch):
    monkeypatch.setenv("AI_SERVICE_KEY", KEY)
    app.dependency_overrides[get_agent] = lambda: GameAgent(provider)
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_health_needs_no_token():
    assert TestClient(app).get("/health").json() == {"ok": True}



def test_generate_without_a_token_is_rejected(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    assert client.post("/generate", json={"prompt": "a coin"}).status_code == 401



def test_generate_with_a_token_returns_objects(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    response = client.post("/generate", json={"prompt": "an enemy at 50 60"}, headers=auth())
    assert response.status_code == 200
    assert response.json() == {"objects": [{"id": "enemy-1", "kind": "enemy", "x": 50.0, "y": 60.0}]}
