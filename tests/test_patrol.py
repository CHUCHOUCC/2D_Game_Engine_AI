import pytest

from app.navigation import OccupancyGrid
from app.navigation.patrol import PatrolRoute
from app.physics import AABB


def open_grid():
    return OccupancyGrid(cols=6, rows=4)


def test_the_route_starts_on_the_first_waypoint():
    route = PatrolRoute(open_grid(), [(0, 0), (3, 0)])
    assert route.current() == (0, 0)


def test_a_lap_goes_out_and_comes_back():
    route = PatrolRoute(open_grid(), [(0, 0), (3, 0)])
    assert route.length() == 6  # 3 tiles out and 3 back, the ends counted once


def test_after_the_last_tile_it_starts_again():
    route = PatrolRoute(open_grid(), [(0, 0), (2, 0)])
    lap = [route.current()] + [route.next_tile() for _ in range(route.length() - 1)]
    assert route.next_tile() == lap[0]
    assert route.next_tile() == lap[1]


def test_every_step_moves_one_tile():
    route = PatrolRoute(open_grid(), [(0, 0), (4, 0), (4, 3)])
    previous = route.current()
    for _ in range(route.length() * 2):
        tile = route.next_tile()
        assert abs(tile[0] - previous[0]) + abs(tile[1] - previous[1]) == 1
        previous = tile


def test_the_route_goes_around_walls():
    grid = OccupancyGrid(cols=5, rows=3)
    grid.block_box(AABB(2 * 32 + 16, 16, 16, 16))
    grid.block_box(AABB(2 * 32 + 16, 48, 16, 16))
    route = PatrolRoute(grid, [(0, 0), (4, 0)])
    tiles = [route.current()] + [route.next_tile() for _ in range(route.length() - 1)]
    assert all(grid.is_free(*tile) for tile in tiles) and (2, 2) in tiles


def test_a_patrol_needs_two_waypoints_and_a_way_between_them():
    with pytest.raises(ValueError):
        PatrolRoute(open_grid(), [(0, 0)])
    grid = OccupancyGrid(cols=3, rows=1)
    grid.block_box(AABB(1 * 32 + 16, 16, 16, 16))
    with pytest.raises(ValueError):
        PatrolRoute(grid, [(0, 0), (2, 0)])
