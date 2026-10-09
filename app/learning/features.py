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
