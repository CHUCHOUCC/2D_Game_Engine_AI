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
