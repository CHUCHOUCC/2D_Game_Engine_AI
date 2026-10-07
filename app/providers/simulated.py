import json
import re

from .base import AiProvider

_KINDS = (
    ("coin", ("coin", "moneda")),
    ("enemy", ("enemy", "enemigo")),
    ("box", ("box", "caja")),
)


class SimulatedProvider(AiProvider):
    """Deterministic stand-in for a real model, for demos and tests (no network, no key).

    It looks for a kind keyword and up to two integers (x, y) in the request and
    answers with the same JSON shape a real model is asked to produce.
    """

    def complete(self, system: str, user: str) -> str:
        text = user.lower()
        kind = next((name for name, words in _KINDS if any(w in text for w in words)), "box")
        numbers = [int(n) for n in re.findall(r"\d+", text)]
        x, y = (numbers[0], numbers[1]) if len(numbers) >= 2 else (100, 100)
        return json.dumps([{"id": f"{kind}-1", "kind": kind, "x": x, "y": y}])
