from app.world import WORLD_HEIGHT, WORLD_WIDTH

from .body import Body


class PhysicsWorld:
    """A tiny Arcade-style physics step: velocity, drag, world bounds and
    collision separation. The AI uses it to check that what it generates
    behaves well before the game ever sees it."""

    def __init__(self, width: float = WORLD_WIDTH, height: float = WORLD_HEIGHT):
        self.width = width
        self.height = height
        self.bodies: list[Body] = []
