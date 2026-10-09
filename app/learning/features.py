from dataclasses import dataclass

from pydantic import BaseModel, Field


class RunSummary(BaseModel):
    """The numbers the backend sends when a run ends (same names as its RunResult)."""

    outcome: str = Field(pattern="^(won|lost|quit)$")
    score: int = Field(ge=0)
    coins_collected: int = Field(ge=0)
    coins_total: int = Field(ge=0)
    enemies_defeated: int = Field(ge=0)
    damage_taken: int = Field(ge=0)
    deaths: int = Field(ge=0)
    duration_ms: int = Field(ge=0)



@dataclass(frozen=True)
class RunFeatures:
    """A run reduced to numbers between 0 and 1 (except seconds and damage)."""

    won: float
    quit: float
    coin_ratio: float
    damage: float
    deaths: float
    seconds: float
    kills: float

    @classmethod
    def of(cls, run: RunSummary) -> "RunFeatures":
        coin_ratio = run.coins_collected / run.coins_total if run.coins_total else 1.0
        return cls(
            won=1.0 if run.outcome == "won" else 0.0,
            quit=1.0 if run.outcome == "quit" else 0.0,
            coin_ratio=min(1.0, coin_ratio),
            damage=float(run.damage_taken),
            deaths=float(run.deaths),
            seconds=run.duration_ms / 1000,
            kills=float(run.enemies_defeated),
        )
