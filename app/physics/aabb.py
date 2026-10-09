from dataclasses import dataclass

from app.world import SIZES

# Boxes closer than this count as just touching (float rounding during separation).
EPSILON = 1e-6


@dataclass(frozen=True)
class AABB:
    """Axis-aligned box given by its centre and half sizes (the same shape Arcade Physics uses)."""

    cx: float
    cy: float
    half_w: float
    half_h: float

    @property
    def left(self) -> float:
        return self.cx - self.half_w

    @property
    def right(self) -> float:
        return self.cx + self.half_w

    @property
    def top(self) -> float:
        return self.cy - self.half_h

    @property
    def bottom(self) -> float:
        return self.cy + self.half_h

    @classmethod
    def of_object(cls, obj: dict) -> "AABB":
        width, height = SIZES.get(obj["kind"], (32, 32))
        return cls(float(obj["x"]), float(obj["y"]), width / 2, height / 2)

    def overlaps(self, other: "AABB", padding: float = 0.0) -> bool:
        """True when the boxes intersect; padding grows both boxes (keeps a gap)."""
        return (
            abs(self.cx - other.cx) < self.half_w + other.half_w + padding - EPSILON
            and abs(self.cy - other.cy) < self.half_h + other.half_h + padding - EPSILON
        )
