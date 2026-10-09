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



def path_length(grid: OccupancyGrid, start: tuple[int, int], goal: tuple[int, int]) -> int | None:
    """Number of steps of the shortest walk from start to goal, or None if blocked."""
    if not grid.is_free(*start) or not grid.is_free(*goal):
        return None
    distance = {start: 0}
    pending = deque([start])
    while pending:
        cell = pending.popleft()
        if cell == goal:
            return distance[cell]
        for dc, dr in NEIGHBOURS:
            nxt = (cell[0] + dc, cell[1] + dr)
            if nxt not in distance and grid.is_free(*nxt):
                distance[nxt] = distance[cell] + 1
                pending.append(nxt)
    return None



def reachable_coin_ids(scene: list, spawn: tuple[float, float]) -> set:
    """Ids of the coins whose tile is reachable from the spawn point."""
    grid = OccupancyGrid.from_scene(scene)
    area = reachable_cells(grid, grid.cell_of(*spawn))
    return {
        str(obj["id"]) for obj in scene
        if obj["kind"] == "coin" and grid.cell_of(obj["x"], obj["y"]) in area
    }
