"""How good the level was, seen from the AI.

The AI does not want players to lose: it wants levels that are hard but fair.
Its reward is highest when the player's performance lands near TARGET.
"""

TARGET_PERFORMANCE = 0.65


def reward(performance: float, target: float = TARGET_PERFORMANCE) -> float:
    """1.0 when performance equals the target, falling linearly to 0.0 at the extremes."""
    spread = max(target, 1.0 - target)
    return round(1.0 - abs(performance - target) / spread, 4)


def reward_with_quit_penalty(performance: float, quit: bool) -> float:
    """Quitting means the level was frustrating or boring: halve the reward."""
    value = reward(performance)
    return round(value / 2, 4) if quit else value
