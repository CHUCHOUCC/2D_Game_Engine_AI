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
