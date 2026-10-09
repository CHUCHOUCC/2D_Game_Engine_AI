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


def test_from_scene_blocks_solids_and_optionally_spikes():
    scene = [{"id": "h", "kind": "house", "x": 144, "y": 144}, {"id": "s", "kind": "spike", "x": 400, "y": 400}]
    assert OccupancyGrid.from_scene(scene).free_count() == 1500 - 9
    assert OccupancyGrid.from_scene(scene, avoid_hazards=True).free_count() == 1500 - 10


def test_reachable_cells_stop_at_walls():
    grid = OccupancyGrid(cols=5, rows=3)
    for row in range(3):
        grid.block_box(AABB(2 * 32 + 16, row * 32 + 16, 16, 16))  # wall in column 2
    area = reachable_cells(grid, (0, 0))
    assert len(area) == 6
    assert (4, 0) not in area
    assert reachable_cells(grid, (2, 0)) == set()


def test_path_length():
    grid = OccupancyGrid(cols=5, rows=3)
    grid.block_box(AABB(2 * 32 + 16, 16, 16, 16))
    grid.block_box(AABB(2 * 32 + 16, 48, 16, 16))
    assert path_length(grid, (0, 0), (4, 0)) == 8
    assert path_length(grid, (0, 0), (0, 0)) == 0
    assert path_length(grid, (0, 0), (2, 0)) is None


def test_reachable_coin_ids():
    walls = [{"id": f"w{r}", "kind": "wall", "x": 336, "y": r * 32 + 16} for r in range(30)]
    coins = [{"id": "near", "kind": "coin", "x": 100, "y": 100}, {"id": "far", "kind": "coin", "x": 800, "y": 100}]
    assert reachable_coin_ids(walls + coins, (50, 50)) == {"near"}
    assert reachable_coin_ids(coins, (50, 50)) == {"near", "far"}
