import hashlib
import json
import math
import random

from app.learning.model import LevelModel
from app.navigation import OccupancyGrid, reachable_cells, reachable_coin_ids
from app.physics import AABB
from app.world import SOLID_KINDS, TILE_SIZE, WORLD_HEIGHT, WORLD_WIDTH

# Never put obstacles right on top of the spawn point.
SPAWN_SAFE_RADIUS = 128
# Enemies start further away so the player has time to react.
ENEMY_SAFE_RADIUS = 256
# Gap kept between a new obstacle and everything already in the scene.
PADDING = 4
CANDIDATES_PER_OBJECT = 60
MAX_COUNT = 30


class ObstacleGenerator:
    """Places new obstacles in a scene following what the model learned.

    Rules every obstacle obeys (checked with the physics boxes and the grid):
    - inside the world, not overlapping anything (AABB with padding);
    - far enough from the player's spawn point;
    - solid obstacles never cut off a coin the player could reach before.
    Higher difficulty puts obstacles closer to the coins and the player's way.
    """

    def __init__(self, model: LevelModel, seed: int | None = None):
        self._model = model
        self._seed = seed

    def _rng_for(self, scene: list, count: int) -> random.Random:
        """Same scene + same model -> same obstacles (easy to test and to explain)."""
        if self._seed is not None:
            return random.Random(self._seed)
        key = json.dumps([scene, count, self._model.to_dict()], sort_keys=True, default=str)
        return random.Random(int(hashlib.sha256(key.encode()).hexdigest()[:16], 16))

    def _pick_kind(self, rng: random.Random) -> str:
        probabilities = self._model.probabilities()
        roll = rng.random()
        for kind, probability in probabilities.items():
            roll -= probability
            if roll <= 0:
                return kind
        return next(reversed(probabilities))

    @staticmethod
    def spawn_of(scene: list) -> tuple[float, float]:
        player = next((obj for obj in scene if obj["kind"] == "player"), None)
        if player is not None:
            return float(player["x"]), float(player["y"])
        return 2 * TILE_SIZE, WORLD_HEIGHT / 2

    @staticmethod
    def _candidate(rng: random.Random, kind: str) -> tuple[float, float]:
        tiles = 3 if kind == "house" else 1
        cols = WORLD_WIDTH // TILE_SIZE - tiles
        rows = WORLD_HEIGHT // TILE_SIZE - tiles
        col = rng.randint(0, cols)
        row = rng.randint(0, rows)
        return (col + tiles / 2) * TILE_SIZE, (row + tiles / 2) * TILE_SIZE

    def _score(self, rng: random.Random, x: float, y: float, coins: list) -> float:
        if not coins:
            return rng.random()
        nearest = min(math.dist((x, y), (c["x"], c["y"])) for c in coins)
        closeness = 1.0 - min(nearest / 600.0, 1.0)
        d = self._model.difficulty
        return d * closeness + (1 - d) * rng.random()

    def _fits(self, obj: dict, boxes: list, spawn: tuple[float, float]) -> bool:
        box = AABB.of_object(obj)
        if not box.inside(WORLD_WIDTH, WORLD_HEIGHT):
            return False
        safe = ENEMY_SAFE_RADIUS if obj["kind"] == "enemy" else SPAWN_SAFE_RADIUS
        if math.dist((obj["x"], obj["y"]), spawn) < safe:
            return False
        return not any(box.overlaps(other, PADDING) for other in boxes)

    @staticmethod
    def _keeps_coins(scene: list, obj: dict, spawn: tuple[float, float], reachable: set) -> bool:
        if obj["kind"] not in SOLID_KINDS or not reachable:
            return True
        return reachable <= reachable_coin_ids(scene + [obj], spawn)

    def generate(self, scene: list, count: int | None = None) -> list:
        """New obstacles for the scene (the scene itself is not changed)."""
        count = self._model.obstacle_budget() if count is None else max(0, min(count, MAX_COUNT))
        rng = self._rng_for(scene, count)
        spawn = self.spawn_of(scene)
        coins = [obj for obj in scene if obj["kind"] == "coin"]
        reachable = reachable_coin_ids(scene, spawn)
        boxes = [AABB.of_object(obj) for obj in scene]
        used_ids = {str(obj["id"]) for obj in scene}
        working = list(scene)
        created = []
        for _ in range(count):
            kind = self._pick_kind(rng)
            options = []
            for _ in range(CANDIDATES_PER_OBJECT):
                x, y = self._candidate(rng, kind)
                candidate = {"id": "", "kind": kind, "x": x, "y": y}
                if self._fits(candidate, boxes, spawn):
                    options.append((self._score(rng, x, y, coins), candidate))
            options.sort(key=lambda option: -option[0])
            # The best few that do not cut a coin off; checking all would be slow.
            obj = next((c for _, c in options[:5] if self._keeps_coins(working, c, spawn, reachable)), None)
            if obj is None:
                continue
            obj["id"] = _new_id(kind, used_ids)
            used_ids.add(obj["id"])
            boxes.append(AABB.of_object(obj))
            working.append(obj)
            created.append(obj)
        return created



def _new_id(kind: str, used: set) -> str:
    n = 1
    while f"ai-{kind}-{n}" in used:
        n += 1
    return f"ai-{kind}-{n}"



def open_area_ratio(scene: list) -> float:
    """Share of the world the player can walk to from the spawn point (0..1)."""
    grid = OccupancyGrid.from_scene(scene)
    spawn = ObstacleGenerator.spawn_of(scene)
    total = grid.cols * grid.rows
    return len(reachable_cells(grid, grid.cell_of(*spawn))) / total
