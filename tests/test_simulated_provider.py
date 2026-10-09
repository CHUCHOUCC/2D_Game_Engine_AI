import json

from app.providers import SimulatedProvider


def ask(text):
    return json.loads(SimulatedProvider().complete("system", f"scene\nRequest: {text}"))


def test_every_kind_keyword():
    words = {"coin": "moneda", "enemy": "enemigo", "house": "casa", "wall": "pared",
             "tree": "arbol", "spike": "pinchos", "box": "caja"}
    for kind, word in words.items():
        assert ask(f"una {word}")[0]["kind"] == kind
