from abc import ABC, abstractmethod


class AiProviderError(Exception):
    """The AI provider failed (network error, bad status or unusable reply)."""


class AiProvider(ABC):
    """Contract every AI provider must follow, so the API behind it can be swapped.

    The agent only knows this interface: changing from the simulated provider
    to a real API means choosing another subclass, not touching the agent.
    """

    @abstractmethod
    def complete(self, system: str, user: str) -> str:
        """Return the model's text reply to the user message, given the system instructions."""
