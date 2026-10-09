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

    def add(self, body: Body) -> Body:
        self.bodies.append(body)
        return body

    @classmethod
    def from_scene(cls, scene: list) -> "PhysicsWorld":
        world = cls()
        for obj in scene:
            world.add(Body.of_object(obj))
        return world
