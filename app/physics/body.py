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
    "dagger": (True, 1.0, 0.0, 0.0),
    "hammer": (True, 1.0, 0.0, 0.0),
    "spear": (True, 1.0, 0.0, 0.0),
    "staff": (True, 1.0, 0.0, 0.0),
    "path": (True, 1.0, 0.0, 0.0),
    "water": (True, 1.0, 0.0, 0.0),
    "sand": (True, 1.0, 0.0, 0.0),
    "bridge": (True, 1.0, 0.0, 0.0),
    "marksman": (False, 1.5, 200.0, 0.2),
    "necromancer": (False, 1.5, 200.0, 0.2),
    "demon": (False, 12.0, 300.0, 0.0),
    "mimic": (False, 1.5, 200.0, 0.2),
    "rat": (False, 0.5, 100.0, 0.3),
    "soldier": (False, 1.5, 200.0, 0.2),
    "grenadier": (False, 1.5, 200.0, 0.2),
    "tank": (False, 14.0, 300.0, 0.0),
    "artillery": (True, 1.0, 0.0, 0.0),
    "legionary": (False, 1.5, 200.0, 0.2),
    "captain": (False, 4.0, 300.0, 0.0),
    "ally": (False, 1.0, 300.0, 0.1),
    "guard": (False, 1.0, 300.0, 0.1),
    "sandbag": (True, 1.0, 0.0, 0.0),
    "barricade": (True, 1.0, 0.0, 0.0),
    "hedgehog": (True, 1.0, 0.0, 0.0),
    "bunker": (True, 1.0, 0.0, 0.0),
    "tower": (True, 1.0, 0.0, 0.0),
    "flag": (True, 1.0, 0.0, 0.0),
    "banner": (True, 1.0, 0.0, 0.0),
    "rock": (True, 1.0, 0.0, 0.0),
    "road": (True, 1.0, 0.0, 0.0),
    "medkit": (True, 1.0, 0.0, 0.0),
    "pistol": (True, 1.0, 0.0, 0.0),
    "rifle": (True, 1.0, 0.0, 0.0),
    "shotgun": (True, 1.0, 0.0, 0.0),
    "smg": (True, 1.0, 0.0, 0.0),
    "sniper": (True, 1.0, 0.0, 0.0),
    "launcher": (True, 1.0, 0.0, 0.0),
    "grenade": (True, 1.0, 0.0, 0.0),
    "explosive": (True, 1.0, 0.0, 0.0),
    "saloon": (True, 1.0, 0.0, 0.0),
    "cabin": (True, 1.0, 0.0, 0.0),
    "wagon": (True, 1.0, 0.0, 0.0),
    "hay": (True, 1.0, 0.0, 0.0),
    "crates": (True, 1.0, 0.0, 0.0),
    "trough": (True, 1.0, 0.0, 0.0),
    "cactus": (True, 1.0, 0.0, 0.0),
    "lamp": (True, 1.0, 0.0, 0.0),
    "boardwalk": (True, 1.0, 0.0, 0.0),
    "dirt": (True, 1.0, 0.0, 0.0),
    "bandit": (False, 1.5, 200.0, 0.2),
}

# Kinds that overlap instead of blocking: pick-ups, traps and enemies that fly or float.
NOT_SOLID = frozenset({
    "coin", "spike", "potion", "sword", "axe", "wand", "bow", "dagger", "hammer", "spear", "staff",
    "bat", "ghost", "path", "sand", "bridge",
    "road", "medkit", "pistol", "rifle", "shotgun", "smg", "sniper", "launcher", "grenade",
    "boardwalk", "dirt",
})


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
