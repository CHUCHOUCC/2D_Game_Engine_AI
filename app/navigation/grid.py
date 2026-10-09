from app.physics.aabb import AABB
from app.world import HAZARD_KINDS, SOLID_KINDS, TILE_SIZE, WORLD_HEIGHT, WORLD_WIDTH


class OccupancyGrid:
    """The world cut into tiles; a tile is blocked when something solid covers it.

    The generator uses it to make sure every coin can still be reached.
    """

    def __init__(self, cols: int = WORLD_WIDTH // TILE_SIZE, rows: int = WORLD_HEIGHT // TILE_SIZE,
                 tile: int = TILE_SIZE):
        self.cols = cols
        self.rows = rows
        self.tile = tile
        self._blocked = [[False] * cols for _ in range(rows)]
