from app.world import (
    ALL_KINDS,
    GENERATED_KINDS,
    OBSTACLE_KINDS,
    SIZES,
    SOLID_KINDS,
    TILE_SIZE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
    inside_world,
)


def test_world_is_a_whole_number_of_tiles():
    assert (WORLD_WIDTH, WORLD_HEIGHT, TILE_SIZE) == (1600, 960, 32)
    assert WORLD_WIDTH % TILE_SIZE == 0 and WORLD_HEIGHT % TILE_SIZE == 0
