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


def test_obstacles_stay_inside_the_world():
    for obj in generate(count=25):
        assert AABB.of_object(obj).inside(WORLD_WIDTH, WORLD_HEIGHT)


def test_spawn_area_is_kept_clear():
    for obj in generate(count=25):
        distance = math.dist((obj["x"], obj["y"]), (PLAYER["x"], PLAYER["y"]))
        assert distance >= (256 if obj["kind"] == "enemy" else 128)


def test_every_coin_stays_reachable():
    objects = generate(count=30, difficulty=0.95)
    spawn = (PLAYER["x"], PLAYER["y"])
    assert reachable_coin_ids(SCENE + objects, spawn) == {c["id"] for c in COINS}


def test_ids_are_unique_and_new():
    existing = SCENE + [{"id": "ai-wall-1", "kind": "wall", "x": 1500, "y": 900}]
    objects = generate(scene=existing, count=15)
    ids = [o["id"] for o in objects]
    assert len(ids) == len(set(ids))
    assert "ai-wall-1" not in ids


def test_same_scene_and_model_give_the_same_obstacles():
    assert generate(count=8) == generate(count=8)
    assert generate(count=8) != generate(count=8, difficulty=0.9)


def test_weights_decide_which_kinds_appear():
    weights = {kind: 0.05 for kind in OBSTACLE_KINDS}
    weights["spike"] = 10
    objects = ObstacleGenerator(LevelModel(weights=weights)).generate(SCENE, 20)
    spikes = sum(1 for o in objects if o["kind"] == "spike")
    assert spikes >= 15


def test_higher_difficulty_places_obstacles_closer_to_coins():
    def mean_distance(objects):
        return sum(min(math.dist((o["x"], o["y"]), (c["x"], c["y"])) for c in COINS) for o in objects) / len(objects)

    easy = mean_distance(generate(count=15, difficulty=0.05))
    hard = mean_distance(generate(count=15, difficulty=0.95))
    assert hard < easy


def test_count_is_capped_and_zero_gives_nothing():
    assert len(generate(count=500)) <= 30
    assert generate(count=0) == []


def test_scene_without_player_uses_the_left_middle_as_spawn():
    assert ObstacleGenerator.spawn_of(COINS) == (64, 480)


def test_open_area_ratio_shrinks_with_walls():
    assert open_area_ratio([]) == 1.0
    walls = [{"id": f"w{r}", "kind": "wall", "x": 816, "y": r * 32 + 16} for r in range(30)]
    assert 0.45 < open_area_ratio(walls) < 0.55
