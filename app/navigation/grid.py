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

    def cell_of(self, x: float, y: float) -> tuple[int, int]:
        col = min(self.cols - 1, max(0, int(x // self.tile)))
        row = min(self.rows - 1, max(0, int(y // self.tile)))
        return col, row

    def center_of(self, col: int, row: int) -> tuple[float, float]:
        return (col + 0.5) * self.tile, (row + 0.5) * self.tile

    def in_bounds(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows

    def is_free(self, col: int, row: int) -> bool:
        return self.in_bounds(col, row) and not self._blocked[row][col]

    def block_box(self, box: AABB) -> None:
        """Block every tile the box covers (touching an edge does not count)."""
        first_col, first_row = self.cell_of(box.left, box.top)
        last_col, last_row = self.cell_of(box.right - 0.01, box.bottom - 0.01)
        for row in range(first_row, last_row + 1):
            for col in range(first_col, last_col + 1):
                self._blocked[row][col] = True
