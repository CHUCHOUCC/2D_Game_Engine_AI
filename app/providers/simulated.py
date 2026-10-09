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
