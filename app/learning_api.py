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



class ObstacleRequest(BaseModel):
    model: dict = Field(default_factory=dict)
    scene: List[SceneObject] = Field(default_factory=list, max_length=MAX_SCENE_OBJECTS)
    count: int | None = Field(default=None, ge=1, le=30)


@router.post("/obstacles")
def obstacles(body: ObstacleRequest):
    model = LevelModel.from_dict(body.model)
    scene = scene_dicts(body.scene)
    objects = ObstacleGenerator(model).generate(scene, body.count)
    return {
        "objects": objects,
        "difficulty": model.difficulty,
        "open_area": round(open_area_ratio(scene + objects), 4),
    }



@router.get("/info")
def info():
    return {
        "world": {"width": WORLD_WIDTH, "height": WORLD_HEIGHT, "tile": TILE_SIZE},
        "kinds": list(ALL_KINDS),
        "sizes": {kind: list(size) for kind, size in SIZES.items()},
        "default_model": LevelModel().to_dict(),
    }
