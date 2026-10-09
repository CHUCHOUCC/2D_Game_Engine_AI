import json

import pytest

from app.agent import AgentError, GameAgent, describe_scene
from app.physics import AABB
from app.providers import AiProvider, SimulatedProvider


class ScriptedProvider(AiProvider):
    """Returns a fixed reply, to test how the agent treats whatever a model says."""

    def __init__(self, reply):
        self._reply = reply
        self.prompts = []

    def complete(self, system, user):
        self.prompts.append((system, user))
        return self._reply


def agent_replying(reply):
    return GameAgent(ScriptedProvider(reply))


def test_simulated_provider_creates_the_requested_object_at_the_given_position():
    objects = GameAgent(SimulatedProvider()).generate("put a coin at 120 340")
    assert objects == [{"id": "coin-1", "kind": "coin", "x": 120.0, "y": 340.0}]



def test_simulated_provider_understands_spanish_keywords():
    objects = GameAgent(SimulatedProvider()).generate("agrega un enemigo")
    assert objects[0]["kind"] == "enemy"



def test_reply_wrapped_in_code_fences_is_accepted():
    reply = '```json\n[{"id": "a", "kind": "box", "x": 100, "y": 200}]\n```'
    assert agent_replying(reply).generate("x")[0]["id"] == "a"



def test_reply_that_is_not_json_is_rejected():
    with pytest.raises(AgentError, match="valid JSON"):
        agent_replying("Sure! Here is your coin.").generate("x")


def test_reply_that_is_not_a_list_is_rejected():
    with pytest.raises(AgentError, match="array"):
        agent_replying('{"id": "a"}').generate("x")



def test_unknown_kind_and_player_are_rejected():
    for kind in ("dragon", "player"):
        reply = json.dumps([{"id": "a", "kind": kind, "x": 100, "y": 100}])
        with pytest.raises(AgentError, match="Unknown kind"):
            agent_replying(reply).generate("x")



def test_out_of_range_position_is_rejected():
    reply = json.dumps([{"id": "a", "kind": "box", "x": 1601, "y": 1}])
    with pytest.raises(AgentError, match="out-of-range"):
        agent_replying(reply).generate("x")
    inside = json.dumps([{"id": "a", "kind": "box", "x": 1500, "y": 900}])
    assert agent_replying(inside).generate("x")



def test_missing_field_and_non_objects_are_rejected():
    with pytest.raises(AgentError):
        agent_replying(json.dumps([{"id": "a", "kind": "box", "x": 1}])).generate("x")
    with pytest.raises(AgentError, match="JSON object"):
        agent_replying("[1, 2]").generate("x")



def test_too_many_objects_are_rejected():
    reply = json.dumps([{"id": str(i), "kind": "box", "x": 100, "y": 100} for i in range(31)])
    with pytest.raises(AgentError, match="Too many"):
        agent_replying(reply).generate("x")



def test_the_scene_is_described_in_the_prompt():
    provider = ScriptedProvider("[]")
    scene = [{"id": "p", "kind": "player", "x": 64, "y": 480}, {"id": "w", "kind": "wall", "x": 300, "y": 300}]
    GameAgent(provider).generate("a coin", scene)
    user = provider.prompts[0][1]
    assert "1 player, 1 wall" in user
    assert "(64, 480)" in user
    assert user.endswith("Request: a coin")


def test_describe_empty_scene():
    assert describe_scene([]) == "The scene is empty."
