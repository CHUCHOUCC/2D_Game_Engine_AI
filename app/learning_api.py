"""Routes of the learning AI: learn from a run, place obstacles, describe the world."""
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from .generation import ObstacleGenerator, open_area_ratio
from .learning import Learner, LevelModel, RunSummary
from .schemas import MAX_SCENE_OBJECTS, SceneObject, scene_dicts
from .security import require_service_token
from .world import ALL_KINDS, SIZES, TILE_SIZE, WORLD_HEIGHT, WORLD_WIDTH

router = APIRouter(dependencies=[Depends(require_service_token)])
