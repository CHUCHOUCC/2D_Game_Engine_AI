import os

from .base import AiProvider, AiProviderError
from .openai_compatible import OpenAiCompatibleProvider
from .simulated import SimulatedProvider

__all__ = ["AiProvider", "AiProviderError", "OpenAiCompatibleProvider", "SimulatedProvider", "create_provider"]


def create_provider(name: str = None) -> AiProvider:
    """Build the provider chosen by AI_PROVIDER ('simulated' by default)."""
    name = (name or os.environ.get("AI_PROVIDER", "simulated")).lower()
    if name == "simulated":
        return SimulatedProvider()
    if name == "openai_compatible":
        return OpenAiCompatibleProvider(
            base_url=os.environ["AI_BASE_URL"],
            api_key=os.environ["AI_API_KEY"],
            model=os.environ["AI_MODEL"],
        )
    raise ValueError(f"Unknown AI_PROVIDER: {name!r}")
