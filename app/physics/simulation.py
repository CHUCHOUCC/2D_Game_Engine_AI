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

    def _integrate(self, body: Body, dt: float) -> None:
        if body.static:
            return
        body.box = body.box.moved(body.vx * dt, body.vy * dt)
        # Linear drag like Arcade Physics: speed drops by drag units per second.
        for axis in ("vx", "vy"):
            speed = getattr(body, axis)
            slowed = max(0.0, abs(speed) - body.drag * dt)
            setattr(body, axis, slowed if speed >= 0 else -slowed)
