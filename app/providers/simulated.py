import json
import re

from app.world import WORLD_HEIGHT, WORLD_WIDTH

from .base import AiProvider

# Keywords per kind, in English and Spanish (with and without accents).
_KINDS = (
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
    # A comma followed by a number belongs to a position like "(90, 70)".
    return [p.strip() for p in re.split(r",(?!\s*\d)|;|\by\b|\band\b", text) if p.strip()]


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
