"""Rules of the game world, shared with the backend and the frontend."""

WORLD_WIDTH = 1600
WORLD_HEIGHT = 960
TILE_SIZE = 32

# Every kind the editor understands. 'player' is the spawn point; the AI never adds one.
ALL_KINDS = (
    "player", "box", "wall", "house", "tree", "spike", "coin", "enemy", "villager", "knight", "wizard",
    "bat", "spider", "ghost", "brute", "chest", "potion", "sword", "axe", "wand", "bow", "barrel", "fence", "bush",
)
# 2D characters: friendly people that walk around and talk. They are never obstacles.
CHARACTER_KINDS = frozenset({"villager", "knight", "wizard"})
# Every kind of enemy; they all chase and hurt the player.
ENEMY_KINDS = frozenset({"enemy", "bat", "spider", "ghost", "brute"})
# Rewards: a chest drops an item; weapons and potions are picked up. Never obstacles.
REWARD_KINDS = frozenset({"chest", "potion", "sword", "axe", "wand", "bow"})
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
    "bat": (24, 20),
    "spider": (26, 24),
    "ghost": (24, 28),
    "brute": (30, 30),
    "chest": (32, 28),
    "potion": (16, 20),
    "sword": (16, 28),
    "axe": (24, 28),
    "wand": (16, 28),
    "bow": (24, 28),
    "barrel": (28, 30),
    "fence": (32, 16),
    "bush": (30, 28),
}

# Enemies that cannot cross walls (bats and ghosts fly over them). In a level
# without coins the player wins by defeating every enemy, so these must stay reachable.
GROUND_ENEMY_KINDS = frozenset({"enemy", "spider", "brute"})
# Kinds the player cannot walk through.
SOLID_KINDS = frozenset({"box", "wall", "house", "tree", "chest", "barrel", "fence", "bush"})
# Kinds that hurt the player.
HAZARD_KINDS = frozenset({"spike"}) | ENEMY_KINDS
# Kinds that are picked up.
COLLECTIBLE_KINDS = frozenset({"coin"})
# Kinds the generator treats as obstacles (everything but coins, rewards and characters).
OBSTACLE_KINDS = tuple(
    kind for kind in GENERATED_KINDS
    if kind not in COLLECTIBLE_KINDS and kind not in CHARACTER_KINDS and kind not in REWARD_KINDS
)


def inside_world(x: float, y: float) -> bool:
    return 0 <= x <= WORLD_WIDTH and 0 <= y <= WORLD_HEIGHT
