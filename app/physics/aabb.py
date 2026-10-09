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

    def penetration(self, other: "AABB") -> tuple[float, float]:
        """Smallest move of self that separates it from other ((0, 0) if they do not touch).

        It pushes along the axis of least overlap, like Arcade Physics' separate().
        """
        dx = other.cx - self.cx
        overlap_x = self.half_w + other.half_w - abs(dx)
        dy = other.cy - self.cy
        overlap_y = self.half_h + other.half_h - abs(dy)
        if overlap_x <= EPSILON or overlap_y <= EPSILON:
            return (0.0, 0.0)
        if overlap_x < overlap_y:
            return (-overlap_x if dx > 0 else overlap_x, 0.0)
        return (0.0, -overlap_y if dy > 0 else overlap_y)

    def moved(self, dx: float, dy: float) -> "AABB":
        return AABB(self.cx + dx, self.cy + dy, self.half_w, self.half_h)

    def inside(self, width: float, height: float) -> bool:
        return self.left >= 0 and self.top >= 0 and self.right <= width and self.bottom <= height
