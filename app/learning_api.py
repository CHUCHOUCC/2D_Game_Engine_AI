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



class LearnRequest(BaseModel):
    model: dict = Field(default_factory=dict)
    run: RunSummary


@router.post("/learn")
def learn(body: LearnRequest):
    """One learning step. The backend stores the returned model and sends it back next time."""
    model, reward = Learner().learn(LevelModel.from_dict(body.model), body.run)
    return {
        "model": model.to_dict(),
        "reward": reward,
        "difficulty": model.difficulty,
        "obstacle_budget": model.obstacle_budget(),
    }
