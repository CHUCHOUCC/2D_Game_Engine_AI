from typing import List

from pydantic import BaseModel, Field

MAX_SCENE_OBJECTS = 1500  # same as the backend: a whole city with its roads


class SceneObject(BaseModel):
    """An object already in the scene, as the backend stores it."""

    id: str = Field(min_length=1, max_length=64)
    kind: str = Field(min_length=1, max_length=20)
    x: float
    y: float


def scene_dicts(objects: List[SceneObject]) -> list:
    return [obj.model_dump() for obj in objects]


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)
    scene: List[SceneObject] = Field(default_factory=list, max_length=MAX_SCENE_OBJECTS)
