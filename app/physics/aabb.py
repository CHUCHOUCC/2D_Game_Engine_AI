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
