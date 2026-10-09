import json
import re
from typing import List

from pydantic import BaseModel, Field, ValidationError

from .physics import Body, PhysicsWorld
from .providers import AiProvider
from .world import GENERATED_KINDS, WORLD_HEIGHT, WORLD_WIDTH

SYSTEM_PROMPT = (
    "You are an assistant that creates objects for a top-down 2D game scene. "
    "Reply with ONLY a JSON array, no explanations. Each element must be "
    f'{{"id": string, "kind": one of {list(GENERATED_KINDS)}, "x": number, "y": number}}. '
    f"x and y are the centre of the object; x is between 0 and {WORLD_WIDTH} and y between 0 and {WORLD_HEIGHT}. "
    "Walls and houses block the way, boxes can be pushed, spikes and enemies hurt, coins are collected."
)



class AgentError(Exception):
    """The model's reply could not be turned into valid game objects."""


class GameObject(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    kind: str
    x: float = Field(ge=0, le=WORLD_WIDTH)
    y: float = Field(ge=0, le=WORLD_HEIGHT)



def describe_scene(scene: list) -> str:
    """A short summary so the model can place objects around what exists."""
    if not scene:
        return "The scene is empty."
    counts = {}
    for obj in scene:
        counts[obj.get("kind", "?")] = counts.get(obj.get("kind", "?"), 0) + 1
    parts = ", ".join(f"{n} {kind}" for kind, n in sorted(counts.items()))
    player = next((o for o in scene if o.get("kind") == "player"), None)
    where = f" The player starts at ({player['x']:.0f}, {player['y']:.0f})." if player else ""
    return f"The scene already has: {parts}.{where} Do not place objects on top of them."



class GameAgent:
    """Turns a natural-language request into validated scene objects.

    Whatever the model answers is untrusted: it is parsed and checked against
    the schema, then the physics engine pushes new objects out of anything
    they overlap before they leave this class.
    """

    MAX_OBJECTS = 30

    def __init__(self, provider: AiProvider):
        self._provider = provider

    def generate(self, request: str, scene: list | None = None) -> List[dict]:
        scene = scene or []
        user = f"{describe_scene(scene)}\nRequest: {request}"
        objects = self._validate(self._provider.complete(SYSTEM_PROMPT, user))
        return self._resolve_overlaps(scene, objects)

    def _validate(self, reply: str) -> List[dict]:
        # Models often wrap JSON in ```json fences; remove them.
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", reply.strip())
        try:
            data = json.loads(text)
        except ValueError as error:
            raise AgentError("The model did not reply with valid JSON") from error
        if not isinstance(data, list):
            raise AgentError("The model reply must be a JSON array")
        if len(data) > self.MAX_OBJECTS:
            raise AgentError(f"Too many objects (max {self.MAX_OBJECTS})")
        objects = []
        for item in data:
            if not isinstance(item, dict):
                raise AgentError("Each element must be a JSON object")
            try:
                obj = GameObject(**item)
            except ValidationError as error:
                raise AgentError("An object has an invalid field or out-of-range value") from error
            if obj.kind not in GENERATED_KINDS:
                raise AgentError(f"Unknown kind: {obj.kind!r}")
            objects.append(obj.model_dump())
        return objects
