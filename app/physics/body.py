from dataclasses import dataclass, field

from .aabb import AABB

# Arcade Physics settings per kind; the frontend uses the same numbers.
# (static, mass, drag, bounce)
KIND_PHYSICS = {
    "player": (False, 1.0, 600.0, 0.0),
    "box": (False, 2.0, 400.0, 0.1),
    "wall": (True, 1.0, 0.0, 0.0),
    "house": (True, 1.0, 0.0, 0.0),
    "tree": (True, 1.0, 0.0, 0.0),
    "spike": (True, 1.0, 0.0, 0.0),
    "coin": (True, 1.0, 0.0, 0.0),
    "enemy": (False, 1.5, 200.0, 0.2),
    "villager": (False, 1.2, 300.0, 0.1),
    "knight": (False, 1.2, 300.0, 0.1),
    "wizard": (False, 1.2, 300.0, 0.1),
    "bat": (False, 0.5, 100.0, 0.3),
    "spider": (False, 1.0, 200.0, 0.2),
    "ghost": (False, 1.0, 100.0, 0.0),
    "brute": (False, 4.0, 300.0, 0.0),
    "chest": (True, 1.0, 0.0, 0.0),
    "potion": (True, 1.0, 0.0, 0.0),
    "sword": (True, 1.0, 0.0, 0.0),
    "axe": (True, 1.0, 0.0, 0.0),
    "wand": (True, 1.0, 0.0, 0.0),
    "bow": (True, 1.0, 0.0, 0.0),
    "barrel": (False, 3.0, 500.0, 0.0),
    "fence": (True, 1.0, 0.0, 0.0),
    "bush": (True, 1.0, 0.0, 0.0),
}

# Kinds that overlap instead of blocking: pick-ups, traps and enemies that fly or float.
NOT_SOLID = frozenset({"coin", "spike", "potion", "sword", "axe", "wand", "bow", "bat", "ghost"})


@dataclass
class Body:
    """A simulated object: its box, velocity and how it reacts to collisions."""

    id: str
    kind: str
    box: AABB
    static: bool = True
    mass: float = 1.0
    drag: float = 0.0
    bounce: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    touching: set = field(default_factory=set)

    @classmethod
    def of_object(cls, obj: dict) -> "Body":
        static, mass, drag, bounce = KIND_PHYSICS.get(obj["kind"], (True, 1.0, 0.0, 0.0))
        return cls(str(obj["id"]), obj["kind"], AABB.of_object(obj), static, mass, drag, bounce)

    @property
    def solid(self) -> bool:
        """Pick-ups, spikes, bats and ghosts overlap the player instead of stopping it."""
        return self.kind not in NOT_SOLID

    def to_object(self) -> dict:
        return {"id": self.id, "kind": self.kind, "x": round(self.box.cx, 1), "y": round(self.box.cy, 1)}
