"""Rules of the game world, shared with the backend and the frontend."""

WORLD_WIDTH = 1600
WORLD_HEIGHT = 960
TILE_SIZE = 32

# Every kind the editor understands. 'player' is the spawn point; the AI never adds one.
ALL_KINDS = ("player", "box", "wall", "house", "tree", "spike", "coin", "enemy")
GENERATED_KINDS = tuple(kind for kind in ALL_KINDS if kind != "player")
