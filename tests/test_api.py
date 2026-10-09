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



def test_generate_moves_objects_off_the_existing_scene(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    scene = [{"id": "w", "kind": "wall", "x": 400, "y": 300}]
    body = {"prompt": "una caja en 400 300", "scene": scene}
    placed = client.post("/generate", json=body, headers=auth()).json()["objects"][0]
    assert (placed["x"], placed["y"]) != (400, 300)



def test_provider_failure_returns_502(monkeypatch):
    client = client_with(FailingProvider(), monkeypatch)
    assert client.post("/generate", json={"prompt": "a coin"}, headers=auth()).status_code == 502



def test_empty_prompt_and_huge_scene_are_rejected(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    assert client.post("/generate", json={"prompt": ""}, headers=auth()).status_code == 422
    scene = [{"id": str(i), "kind": "box", "x": 1, "y": 1} for i in range(601)]
    assert client.post("/generate", json={"prompt": "x", "scene": scene}, headers=auth()).status_code == 422
