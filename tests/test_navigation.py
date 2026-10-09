from app.navigation import OccupancyGrid, path_length, reachable_cells, reachable_coin_ids
from app.physics import AABB


def test_cell_of_and_center_of():
    grid = OccupancyGrid()
    assert (grid.cols, grid.rows) == (50, 30)
    assert grid.cell_of(0, 0) == (0, 0)
    assert grid.cell_of(33, 65) == (1, 2)
    assert grid.cell_of(99999, -5) == (49, 0)
    assert grid.center_of(1, 2) == (48, 80)
