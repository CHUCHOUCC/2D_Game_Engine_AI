import json
import re

from app.world import WORLD_HEIGHT, WORLD_WIDTH

from .base import AiProvider

# Keywords per kind, in English and Spanish (with and without accents).
_KINDS = (
    ("villager", ("villager", "aldeano", "campesino")),
    ("knight", ("knight", "caballero", "guerrero")),
    ("wizard", ("wizard", "mago", "hechicero")),
    ("coin", ("coin", "moneda")),
    ("enemy", ("enemy", "enemies", "enemigo", "slime", "monstruo")),
    ("house", ("house", "casa")),
    ("wall", ("wall", "pared", "muro")),
    ("tree", ("tree", "arbol", "árbol")),
    ("spike", ("spike", "pincho", "trampa")),
    ("box", ("box", "caja")),
)

_NUMBER_WORDS = {
    "un": 1, "una": 1, "uno": 1, "a": 1, "an": 1, "one": 1,
    "dos": 2, "two": 2, "tres": 3, "three": 3, "cuatro": 4, "four": 4,
    "cinco": 5, "five": 5, "seis": 6, "six": 6, "diez": 10, "ten": 10,
}
MAX_PER_KIND = 10


def _parts(text: str) -> list:
    """'3 coins and a wall at 400 300' -> ['3 coins', 'a wall at 400 300']."""
    # A comma between two numbers belongs to a position like "(90, 70)";
    # any other comma ("un aldeano, 2 caballeros") separates two requests.
    return [p.strip() for p in re.split(r"(?<!\d),|,(?!\s*\d)|;|\by\b|\band\b", text) if p.strip()]


def _kind_of(part: str):
    return next((name for name, words in _KINDS if any(w in part for w in words)), None)


def _count_of(part: str, kind_word_at: int) -> int:
    before = part[:kind_word_at].split()
    if before:
        last = before[-1]
        if last.isdigit():
            return max(1, min(int(last), MAX_PER_KIND))
        if last in _NUMBER_WORDS:
            return _NUMBER_WORDS[last]
    return 1


def _position_of(part: str):
    match = re.search(r"(?:at|en|in)\s+\(?\s*(\d+)\s*[, ]\s*(\d+)", part)
    if match:
        return min(int(match.group(1)), WORLD_WIDTH), min(int(match.group(2)), WORLD_HEIGHT)
    return None


class SimulatedProvider(AiProvider):
    """Deterministic stand-in for a real model, for demos and tests (no network, no key).

    It understands requests like "3 monedas y una pared en 400 300": one kind per
    part, an optional count and an optional position. Without a position the
    objects are laid out in a row in the middle of the world.
    """

    def complete(self, system: str, user: str) -> str:
        request = user.split("Request:", 1)[-1].lower()
        objects = []
        for part in _parts(request) or [request]:
            kind = _kind_of(part)
            if kind is None:
                continue
            word_at = min(part.find(w) for w in dict(_KINDS)[kind] if w in part)
            count = _count_of(part, word_at)
            position = _position_of(part)
            for i in range(count):
                if position:
                    x, y = position[0] + 40 * i, position[1]
                else:
                    x, y = WORLD_WIDTH / 2 - 40 * (count - 1) / 2 + 40 * i, WORLD_HEIGHT / 2
                objects.append({"id": f"{kind}-{len(objects) + 1}", "kind": kind,
                                "x": min(x, WORLD_WIDTH), "y": y})
        if not objects:
            objects.append({"id": "box-1", "kind": "box", "x": WORLD_WIDTH / 2, "y": WORLD_HEIGHT / 2})
        return json.dumps(objects)
