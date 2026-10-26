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


def test_the_ai_never_generates_a_player():
    assert "player" in ALL_KINDS
    assert "player" not in GENERATED_KINDS
    assert "coin" not in OBSTACLE_KINDS


def test_every_kind_has_a_size_and_solids_are_known_kinds():
    assert set(SIZES) == set(ALL_KINDS)
    assert SOLID_KINDS <= set(ALL_KINDS)


def test_inside_world():
    assert inside_world(0, 0) and inside_world(1600, 960)
    assert not inside_world(-1, 5) and not inside_world(5, 961)


def test_characters_can_be_generated_but_are_never_obstacles():
    from app.world import CHARACTER_KINDS

    assert CHARACTER_KINDS <= set(GENERATED_KINDS)
    assert not CHARACTER_KINDS & set(OBSTACLE_KINDS)


def test_rewards_and_new_enemies():
    from app.world import ENEMY_KINDS, HAZARD_KINDS, REWARD_KINDS, SOLID_KINDS

    assert not REWARD_KINDS & set(OBSTACLE_KINDS)
    assert ENEMY_KINDS <= HAZARD_KINDS
    assert {"bat", "spider", "ghost", "brute", "barrel", "fence", "bush"} <= set(OBSTACLE_KINDS)
    assert "chest" in SOLID_KINDS
