from app.structures import CircularLinkedList

from .grid import OccupancyGrid
from .pathfinding import shortest_path


class PatrolRoute:
    """The tiles an enemy walks on a round: from waypoint to waypoint and back to the first, forever.

    The tiles live in a CircularLinkedList, so after the last tile of the lap the
    next one is the first again and the enemy never needs a "reached the end" case.
    """

    def __init__(self, grid: OccupancyGrid, waypoints):
        points = list(waypoints)
        if len(points) < 2:
            raise ValueError("a patrol needs at least two waypoints")
        self._tiles = CircularLinkedList()
        for start, goal in zip(points, points[1:] + points[:1]):
            leg = shortest_path(grid, start, goal)
            if leg is None:
                raise ValueError(f"no walkable path from {start} to {goal}")
            for tile in leg[:-1]:  # the goal is the first tile of the next leg
                self._tiles.add(tile)

    def current(self) -> tuple:
        return self._tiles.current()

    def next_tile(self) -> tuple:
        """Move on one tile and return it; after the last tile of the lap it is the first again."""
        return self._tiles.advance()

    def length(self) -> int:
        """Number of tiles of one lap."""
        return self._tiles.size()
