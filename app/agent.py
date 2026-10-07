import json
import re
from typing import List

from pydantic import BaseModel, Field, ValidationError

from .providers import AiProvider

ALLOWED_KINDS = ("box", "coin", "enemy")
SCENE_WIDTH = 800
SCENE_HEIGHT = 600

SYSTEM_PROMPT = (
    "You are an assistant that creates objects for a 2D game scene. "
    f"Reply with ONLY a JSON array, no explanations. Each element must be "
    f'{{"id": string, "kind": one of {list(ALLOWED_KINDS)}, "x": number, "y": number}}. '
    f"x is between 0 and {SCENE_WIDTH} and y between 0 and {SCENE_HEIGHT}."
)


class AgentError(Exception):
    """The model's reply could not be turned into valid game objects."""


class GameObject(BaseModel):
    id: str = Field(min_length=1)
    kind: str
    x: float = Field(ge=0, le=SCENE_WIDTH)
    y: float = Field(ge=0, le=SCENE_HEIGHT)


class GameAgent:
    """Turns a natural-language request into validated scene objects.

    Whatever the model answers is untrusted: it is parsed and checked against
    the schema before anything leaves this class.
    """

    MAX_OBJECTS = 20

    def __init__(self, provider: AiProvider):
        self._provider = provider

    def generate(self, request: str) -> List[dict]:
        reply = self._provider.complete(SYSTEM_PROMPT, request)
        return self._validate(reply)

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
            try:
                obj = GameObject(**item) if isinstance(item, dict) else None
            except ValidationError as error:
                raise AgentError("An object has an invalid field or out-of-range value") from error
            if obj is None:
                raise AgentError("Each element must be a JSON object")
            if obj.kind not in ALLOWED_KINDS:
                raise AgentError(f"Unknown kind: {obj.kind!r}")
            objects.append(obj.model_dump())
        return objects
