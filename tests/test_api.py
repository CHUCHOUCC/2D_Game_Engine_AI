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
