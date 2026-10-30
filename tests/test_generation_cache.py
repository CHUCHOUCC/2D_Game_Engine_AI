from fastapi.testclient import TestClient

from app.agent import GameAgent
from app.cache import generation_key
from app.main import app, get_agent
from app.providers import AiProvider, AiProviderError, SimulatedProvider
from tests.tokens import KEY, auth


class CountingProvider(SimulatedProvider):
    calls = 0

    def complete(self, system, user):
        CountingProvider.calls += 1
        return super().complete(system, user)


class FailingOnce(AiProvider):
    failed = False

    def complete(self, system, user):
        if not FailingOnce.failed:
            FailingOnce.failed = True
            raise AiProviderError("down")
        return SimulatedProvider().complete(system, user)


def client_with(provider, monkeypatch):
    monkeypatch.setenv("AI_SERVICE_KEY", KEY)
    app.dependency_overrides[get_agent] = lambda: GameAgent(provider)
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_the_same_prompt_on_the_same_scene_calls_the_ai_once(monkeypatch):
    CountingProvider.calls = 0
    client = client_with(CountingProvider(), monkeypatch)
    first = client.post("/generate", json={"prompt": "an enemy at 50 60"}, headers=auth())
    second = client.post("/generate", json={"prompt": "  An   enemy at 50 60 "}, headers=auth())
    assert first.json() == second.json()
    assert (first.headers["x-cache"], second.headers["x-cache"]) == ("MISS", "HIT")
    assert CountingProvider.calls == 1


def test_a_different_scene_is_a_different_answer(monkeypatch):
    CountingProvider.calls = 0
    client = client_with(CountingProvider(), monkeypatch)
    client.post("/generate", json={"prompt": "a coin"}, headers=auth())
    scene = [{"id": "w", "kind": "wall", "x": 0, "y": 0}]
    response = client.post("/generate", json={"prompt": "a coin", "scene": scene}, headers=auth())
    assert response.headers["x-cache"] == "MISS"
    assert CountingProvider.calls == 2


def test_errors_are_not_cached(monkeypatch):
    FailingOnce.failed = False
    client = client_with(FailingOnce(), monkeypatch)
    assert client.post("/generate", json={"prompt": "a coin"}, headers=auth()).status_code == 502
    retry = client.post("/generate", json={"prompt": "a coin"}, headers=auth())
    assert retry.status_code == 200 and retry.headers["x-cache"] == "MISS"


def test_cached_objects_are_copies():
    from app.cache import cached_generation

    provider = SimulatedProvider()
    objects, _ = cached_generation(provider, "x", [], lambda: [{"id": "a", "x": 1}])
    objects[0]["x"] = 999
    again, hit = cached_generation(provider, "x", [], lambda: [])
    assert hit and again == [{"id": "a", "x": 1}]


def test_the_key_depends_on_provider_prompt_and_scene():
    simulated = SimulatedProvider()
    base = generation_key(simulated, "a coin", [])
    assert base == generation_key(simulated, "A  COIN", [])
    assert base != generation_key(simulated, "two coins", [])
    assert base != generation_key(simulated, "a coin", [{"id": "w"}])
    assert base != generation_key(CountingProvider(), "a coin", [])
