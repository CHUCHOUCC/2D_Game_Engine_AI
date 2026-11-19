from fastapi.testclient import TestClient

from app.agent import GameAgent
from app.edits import normalise, parse_edit, removed_ids
from app.main import app, get_agent
from app.providers import AiProvider, SimulatedProvider
from app.world import ALL_KINDS, ENEMY_KINDS
from tests.tokens import KEY, auth

SCENE = [
    {"id": "p", "kind": "player", "x": 100, "y": 100},
    {"id": "e1", "kind": "enemy", "x": 300, "y": 300},
    {"id": "t1", "kind": "tank", "x": 500, "y": 300},
    {"id": "c1", "kind": "coin", "x": 200, "y": 200},
    {"id": "c2", "kind": "coin", "x": 220, "y": 200},
    {"id": "w1", "kind": "wall", "x": 600, "y": 600},
    {"id": "r1", "kind": "rifle", "x": 700, "y": 600},
    {"id": "v1", "kind": "villager", "x": 800, "y": 600},
    {"id": "k1", "kind": "explosive", "x": 900, "y": 600},
]


def kinds_removed(prompt: str) -> set:
    edit = parse_edit(prompt)
    return {obj["kind"] for obj in SCENE if obj["id"] in set(removed_ids(SCENE, edit.remove_kinds))}


def test_normalise_drops_accents_and_case():
    assert normalise("  Elimína   TODO  ") == "elimina todo"


def test_remove_everything_keeps_the_player():
    for prompt in ("elimina todo", "Borra todo el mapa", "limpia la escena", "delete everything", "vacía el nivel"):
        assert kinds_removed(prompt) == {k for k in (o["kind"] for o in SCENE)} - {"player"}, prompt


def test_remove_enemies_only():
    for prompt in ("borra los enemigos", "elimina todos los enemigos", "quita a los monstruos", "remove the enemies"):
        assert kinds_removed(prompt) == {"enemy", "tank"}, prompt


def test_remove_objects_means_the_pickups():
    assert kinds_removed("borra los objetos") == {"coin", "rifle"}


def test_remove_named_kinds_and_lists():
    assert kinds_removed("quita las monedas") == {"coin"}
    assert kinds_removed("borra los enemigos y las monedas") == {"enemy", "tank", "coin"}
    assert kinds_removed("elimina los barriles explosivos") == {"explosive"}
    assert kinds_removed("borra el tanque") == {"tank"}


def test_remove_and_add_in_one_request():
    edit = parse_edit("borra todo y pon 5 tanques")
    assert edit.remove_kinds == set(ALL_KINDS) - {"player"}
    assert edit.add_request == "pon 5 tanques"


def test_a_request_without_removal_is_left_to_the_model():
    edit = parse_edit("Pon 3 árboles y un cofre")
    assert not edit.removes and edit.add_request == "Pon 3 árboles y un cofre"


def test_the_player_goes_only_when_named():
    assert "player" in kinds_removed("borra el jugador")
    assert "player" not in kinds_removed("borra todo")


class NeverCalled(AiProvider):
    def complete(self, system, user):
        raise AssertionError("a removal must not call the model")


def client_with(provider, monkeypatch):
    monkeypatch.setenv("AI_SERVICE_KEY", KEY)
    app.dependency_overrides[get_agent] = lambda: GameAgent(provider)
    return TestClient(app)


def teardown_function():
    app.dependency_overrides.clear()


def test_endpoint_removes_without_calling_the_model(monkeypatch):
    client = client_with(NeverCalled(), monkeypatch)
    reply = client.post("/generate", json={"prompt": "borra los enemigos", "scene": SCENE}, headers=auth())
    assert reply.status_code == 200
    assert reply.json() == {"objects": [], "removed": ["e1", "t1"]}


def test_endpoint_removes_then_adds_on_the_cleared_scene(monkeypatch):
    client = client_with(SimulatedProvider(), monkeypatch)
    reply = client.post("/generate", json={"prompt": "elimina todo y pon 2 monedas", "scene": SCENE}, headers=auth())
    assert reply.status_code == 200
    body = reply.json()
    assert set(body["removed"]) == {o["id"] for o in SCENE} - {"p"}
    assert [o["kind"] for o in body["objects"]] == ["coin", "coin"]
    assert all(o["kind"] not in ENEMY_KINDS for o in body["objects"])
