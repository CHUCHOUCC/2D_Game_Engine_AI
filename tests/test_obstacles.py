import math

from app.generation import ObstacleGenerator, open_area_ratio
from app.learning import LevelModel
from app.navigation import reachable_coin_ids
from app.physics import AABB
from app.world import OBSTACLE_KINDS, WORLD_HEIGHT, WORLD_WIDTH

PLAYER = {"id": "hero", "kind": "player", "x": 64, "y": 480}
COINS = [{"id": f"c{i}", "kind": "coin", "x": 300 + 250 * i, "y": 480} for i in range(5)]
SCENE = [PLAYER] + COINS


def generate(scene=SCENE, count=10, **model):
    return ObstacleGenerator(LevelModel(**model)).generate(scene, count)


def test_generates_the_requested_number_of_obstacles():
    objects = generate(count=10)
    assert len(objects) == 10
    assert all(obj["kind"] in OBSTACLE_KINDS for obj in objects)



def test_default_count_is_the_model_budget():
    model = LevelModel(difficulty=0.95)
    assert len(ObstacleGenerator(model).generate(SCENE)) == model.obstacle_budget()



def test_obstacles_never_overlap_each_other_or_the_scene():
    objects = generate(count=25)
    boxes = [AABB.of_object(o) for o in SCENE + objects]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            assert not a.overlaps(b)
