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
