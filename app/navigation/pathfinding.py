from collections import deque

from .grid import OccupancyGrid

NEIGHBOURS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def reachable_cells(grid: OccupancyGrid, start: tuple[int, int]) -> set:
    """Every free tile the player can walk to from start (4-way moves)."""
    if not grid.is_free(*start):
        return set()
    seen = {start}
    pending = deque([start])
    while pending:
        col, row = pending.popleft()
        for dc, dr in NEIGHBOURS:
            cell = (col + dc, row + dr)
            if cell not in seen and grid.is_free(*cell):
                seen.add(cell)
                pending.append(cell)
    return seen
