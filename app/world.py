"""Rules of the game world, shared with the backend and the frontend."""

WORLD_WIDTH = 1600
WORLD_HEIGHT = 960
TILE_SIZE = 32

# Every kind the editor understands. 'player' is the spawn point; the AI never adds one.
ALL_KINDS = (
    "player", "box", "wall", "house", "tree", "spike", "coin", "enemy", "villager", "knight", "wizard",
    "bat", "spider", "ghost", "brute", "chest", "potion", "sword", "axe", "wand", "bow", "barrel", "fence", "bush",
    "dagger", "hammer", "spear", "staff", "path",
    "water", "sand", "bridge", "marksman", "necromancer", "demon", "mimic", "rat",
    "soldier", "grenadier", "tank", "artillery", "ally", "sandbag", "barricade", "hedgehog", "bunker", "tower",
    "flag", "banner", "rock", "road", "medkit", "legionary", "captain", "guard",
    "pistol", "rifle", "shotgun", "smg", "sniper", "launcher", "grenade", "explosive",
    # the Western town
    "saloon", "cabin", "wagon", "hay", "crates", "trough", "cactus", "lamp", "boardwalk", "dirt", "bandit",
    # the industrial arena
    "metalfloor", "hazard", "steelwall", "container", "pipes", "reactor", "beacon", "barrier", "turret", "drone",
)
# 2D characters: friendly people that walk around and talk. They are never obstacles.
CHARACTER_KINDS = frozenset({"villager", "knight", "wizard", "ally", "guard"})
# Every kind of enemy; they all chase and hurt the player.
ENEMY_KINDS = frozenset({
    "enemy", "bat", "spider", "ghost", "brute", "marksman", "necromancer", "demon", "mimic", "rat",
    "soldier", "grenadier", "tank", "artillery", "legionary", "captain", "bandit", "turret", "drone",
})
# Rewards: a chest drops an item; weapons and potions are picked up. Never obstacles.
REWARD_KINDS = frozenset({
    "chest", "potion", "sword", "axe", "wand", "bow", "dagger", "hammer", "spear", "staff",
    "medkit", "pistol", "rifle", "shotgun", "smg", "sniper", "launcher", "grenade",
})
# Ground drawn under everything (roads, stone): no body, never an obstacle.
GROUND_KINDS = frozenset({"path", "sand", "bridge", "road", "boardwalk", "dirt", "metalfloor", "hazard"})
# Terrain painted tile by tile (water): solid for walking, but never a random obstacle.
TERRAIN_KINDS = frozenset({"water"})
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
    "dagger": (16, 24),
    "hammer": (24, 28),
    "spear": (16, 32),
    "staff": (16, 32),
    "path": (32, 32),
    "water": (32, 32),
    "sand": (32, 32),
    "bridge": (32, 32),
    "marksman": (24, 28),
    "necromancer": (24, 28),
    "demon": (56, 56),
    "mimic": (30, 28),
    "rat": (24, 20),
    "soldier": (24, 28),
    "grenadier": (24, 28),
    "tank": (52, 44),
    "artillery": (30, 28),
    "ally": (24, 28),
    "sandbag": (32, 20),
    "barricade": (32, 30),
    "hedgehog": (30, 28),
    "bunker": (32, 32),
    "tower": (28, 32),
    "flag": (20, 30),
    "banner": (20, 30),
    "rock": (30, 28),
    "road": (32, 32),
    "medkit": (20, 18),
    "legionary": (24, 30),
    "captain": (26, 28),
    "guard": (24, 28),
    "pistol": (24, 18),
    "rifle": (32, 14),
    "shotgun": (32, 14),
    "smg": (26, 20),
    "sniper": (32, 14),
    "launcher": (32, 16),
    "grenade": (18, 20),
    "explosive": (28, 30),
    "saloon": (160, 128),
    "cabin": (96, 96),
    "wagon": (64, 48),
    "hay": (32, 32),
    "crates": (64, 48),
    "trough": (64, 32),
    "cactus": (32, 48),
    "lamp": (32, 64),
    "boardwalk": (32, 32),
    "dirt": (32, 32),
    "bandit": (24, 28),
    "metalfloor": (32, 32),
    "hazard": (32, 32),
    "steelwall": (32, 32),
    "container": (64, 32),
    "pipes": (64, 32),
    "reactor": (64, 64),
    "beacon": (32, 48),
    "barrier": (32, 16),
    "turret": (32, 28),
    "drone": (24, 24),
}

# Enemies that cannot cross walls (bats and ghosts fly over them). In a level
# without coins the player wins by defeating every enemy, so these must stay reachable.
GROUND_ENEMY_KINDS = frozenset({
    "enemy", "spider", "brute", "marksman", "necromancer", "demon", "mimic", "rat",
    "soldier", "grenadier", "tank", "artillery", "legionary", "captain", "bandit", "turret",
})
# Kinds the player cannot walk through.
SOLID_KINDS = frozenset({
    "box", "wall", "house", "tree", "chest", "barrel", "fence", "bush", "water",
    "sandbag", "barricade", "hedgehog", "bunker", "tower", "flag", "banner", "rock", "explosive",
    "saloon", "cabin", "wagon", "hay", "crates", "trough", "cactus", "lamp",
    "steelwall", "container", "pipes", "reactor", "beacon", "barrier",
})
# Kinds that hurt the player.
HAZARD_KINDS = frozenset({"spike", "explosive"}) | ENEMY_KINDS
# Kinds that are picked up.
COLLECTIBLE_KINDS = frozenset({"coin"})
# Kinds the generator treats as obstacles (everything but coins, rewards, characters and ground).
OBSTACLE_KINDS = tuple(
    kind for kind in GENERATED_KINDS
    if kind not in COLLECTIBLE_KINDS and kind not in CHARACTER_KINDS and kind not in REWARD_KINDS
    and kind not in GROUND_KINDS and kind not in TERRAIN_KINDS
)


def inside_world(x: float, y: float) -> bool:
    return 0 <= x <= WORLD_WIDTH and 0 <= y <= WORLD_HEIGHT
