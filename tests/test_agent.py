import json

import pytest

from app.agent import AgentError, GameAgent
from app.providers import AiProvider, SimulatedProvider


class ScriptedProvider(AiProvider):
    """Returns a fixed reply, to test how the agent treats whatever a model says."""

    def __init__(self, reply):
        self._reply = reply

    def complete(self, system, user):
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
    reply = '```json\n[{"id": "a", "kind": "box", "x": 1, "y": 2}]\n```'
    assert agent_replying(reply).generate("x")[0]["id"] == "a"


def test_reply_that_is_not_json_is_rejected():
    with pytest.raises(AgentError, match="valid JSON"):
        agent_replying("Sure! Here is your coin.").generate("x")


def test_reply_that_is_not_a_list_is_rejected():
    with pytest.raises(AgentError, match="array"):
        agent_replying('{"id": "a"}').generate("x")


def test_unknown_kind_is_rejected():
    reply = json.dumps([{"id": "a", "kind": "dragon", "x": 1, "y": 1}])
    with pytest.raises(AgentError, match="Unknown kind"):
        agent_replying(reply).generate("x")


def test_out_of_range_position_is_rejected():
    reply = json.dumps([{"id": "a", "kind": "box", "x": 5000, "y": 1}])
    with pytest.raises(AgentError, match="out-of-range"):
        agent_replying(reply).generate("x")


def test_missing_field_is_rejected():
    reply = json.dumps([{"id": "a", "kind": "box", "x": 1}])
    with pytest.raises(AgentError):
        agent_replying(reply).generate("x")


def test_too_many_objects_are_rejected():
    reply = json.dumps([{"id": str(i), "kind": "box", "x": 1, "y": 1} for i in range(21)])
    with pytest.raises(AgentError, match="Too many"):
        agent_replying(reply).generate("x")
