from app.navigation import OccupancyGrid, path_length, reachable_cells, reachable_coin_ids
from app.physics import AABB


def test_cell_of_and_center_of():
    grid = OccupancyGrid()
    assert (grid.cols, grid.rows) == (50, 30)
    assert grid.cell_of(0, 0) == (0, 0)
    assert grid.cell_of(33, 65) == (1, 2)
    assert grid.cell_of(99999, -5) == (49, 0)
    assert grid.center_of(1, 2) == (48, 80)



def test_block_box_covers_only_the_tiles_under_it():
    grid = OccupancyGrid()
    grid.block_box(AABB(48, 48, 16, 16))  # exactly tile (1, 1)
    assert not grid.is_free(1, 1)
    assert grid.is_free(0, 1) and grid.is_free(2, 1) and grid.is_free(1, 2)
    assert grid.free_count() == 50 * 30 - 1
