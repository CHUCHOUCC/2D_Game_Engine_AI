"""Rules of the game world, shared with the backend and the frontend."""

WORLD_WIDTH = 1600
WORLD_HEIGHT = 960
TILE_SIZE = 32

# Every kind the editor understands. 'player' is the spawn point; the AI never adds one.
ALL_KINDS = ("player", "box", "wall", "house", "tree", "spike", "coin", "enemy", "villager", "knight", "wizard")
# 2D characters: friendly people that walk around and talk. They are never obstacles.
CHARACTER_KINDS = frozenset({"villager", "knight", "wizard"})
GENERATED_KINDS = tuple(kind for kind in ALL_KINDS if kind != "player")

# Width and height of each kind in pixels; x and y of an object are its centre.
SIZES = {
    "player": (24, 24),
    "box": (32, 32),
    "wall": (32, 32),
    "house": (96, 96),
    "tree": (32, 32),
    "spike": (32, 32),
    "coin": (16, 16),
    "enemy": (28, 28),
    "villager": (24, 28),
    "knight": (24, 28),
    "wizard": (24, 28),
}

# Kinds the player cannot walk through.
SOLID_KINDS = frozenset({"box", "wall", "house", "tree"})
# Kinds that hurt the player.
HAZARD_KINDS = frozenset({"spike", "enemy"})
# Kinds that are picked up.
COLLECTIBLE_KINDS = frozenset({"coin"})
# Kinds the generator treats as obstacles (everything but coins and characters).
OBSTACLE_KINDS = tuple(
    kind for kind in GENERATED_KINDS if kind not in COLLECTIBLE_KINDS and kind not in CHARACTER_KINDS
)


def inside_world(x: float, y: float) -> bool:
    return 0 <= x <= WORLD_WIDTH and 0 <= y <= WORLD_HEIGHT
