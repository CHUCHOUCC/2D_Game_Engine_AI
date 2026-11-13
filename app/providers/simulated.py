import json
import math
import re

from app.world import SIZES, WORLD_HEIGHT, WORLD_WIDTH

from .base import AiProvider

# Keywords per kind, in English and Spanish (with and without accents).
_KINDS = (
    ("explosive", ("explosive barrel", "barril explosivo", "barriles explosivos", "polvorin", "polvorín")),
    # The industrial arena (before "muro", "pared" and "suelo").
    ("turret", ("turret", "torreta")),
    ("drone", ("drone", "dron")),
    ("metalfloor", ("metal floor", "suelo de metal", "placas de metal")),
    ("hazard", ("hazard", "franja de peligro", "franjas de peligro")),
    ("steelwall", ("steel wall", "muro de acero", "muros de acero", "pared de acero", "muro metálico", "muro metalico")),
    ("container", ("container", "contenedor")),
    ("pipes", ("pipe", "tubería", "tuberia", "tubo")),
    ("reactor", ("reactor", "generador", "núcleo", "nucleo")),
    ("beacon", ("beacon", "baliza")),
    ("barrier", ("barrier", "barrera")),
    # The Western town (before "casa", "caja" and "camino", which they contain).
    ("bandit", ("bandit", "outlaw", "bandido", "pistolero", "forajido")),
    ("saloon", ("saloon", "cantina")),
    ("cabin", ("cabin", "cabaña", "cabana")),
    ("wagon", ("wagon", "carreta", "carro")),
    ("hay", ("hay", "heno", "fardo", "paja")),
    ("crates", ("crates", "pila de cajas", "cajas apiladas")),
    ("trough", ("trough", "abrevadero")),
    ("cactus", ("cactus", "saguaro")),
    ("lamp", ("lamp", "farol", "farola")),
    ("boardwalk", ("boardwalk", "pasarela", "tablones")),
    ("dirt", ("dirt", "tierra")),
    ("artillery", ("artillery", "artilleria", "artillería", "cañon", "cañón", "canon")),
    ("tank", ("tank", "tanque")),
    ("grenadier", ("grenadier", "granadero")),
    ("grenade", ("grenade", "granada", "granadas")),
    ("soldier", ("soldier", "fusilero", "soldado enemigo", "soldados enemigos")),
    ("legionary", ("legionary", "legionario")),
    ("captain", ("captain", "capitan", "capitán", "oficial")),
    ("ally", ("ally", "aliado", "aliados", "soldado aliado")),
    ("guard", ("guard", "guardia", "centinela")),
    ("sandbag", ("sandbag", "sacos terreros", "saco terrero", "trinchera")),
    ("barricade", ("barricade", "barricada")),
    ("hedgehog", ("hedgehog", "erizo", "antitanque")),
    ("bunker", ("bunker", "búnker")),
    ("tower", ("tower", "torre")),
    ("banner", ("banner", "estandarte")),
    ("flag", ("flag", "bandera")),
    ("rock", ("rock", "colina", "roca")),
    ("road", ("road", "carretera", "asfalto")),
    ("medkit", ("medkit", "botiquin", "botiquín")),
    ("sniper", ("sniper", "francotirador")),
    ("launcher", ("launcher", "lanzacohetes", "bazooka", "rpg")),
    ("shotgun", ("shotgun", "escopeta")),
    ("smg", ("smg", "subfusil", "metralleta", "ametralladora")),
    ("rifle", ("rifle", "fusil")),
    ("pistol", ("pistol", "pistola", "revolver", "revólver")),
    ("villager", ("villager", "aldeano", "campesino")),
    ("knight", ("knight", "caballero", "guerrero")),
    ("wizard", ("wizard", "mago", "hechicero")),
    ("bat", ("bat", "murcielago", "murciélago")),
    ("spider", ("spider", "araña", "arana")),
    ("ghost", ("ghost", "fantasma")),
    ("brute", ("brute", "ogro", "ciclope", "cíclope")),
    ("chest", ("chest", "cofre")),
    ("potion", ("potion", "pocion", "poción")),
    ("sword", ("sword", "espada")),
    ("axe", ("axe", "hacha")),
    ("wand", ("wand", "varita")),
    ("bow", ("bow", "arco")),
    ("dagger", ("dagger", "daga", "dagas", "cuchillo")),
    ("hammer", ("hammer", "martillo")),
    ("spear", ("spear", "lanza")),
    ("staff", ("staff", "baculo", "báculo", "baston", "bastón")),
    ("path", ("path", "road", "camino", "calle", "sendero")),
    ("water", ("water", "agua", "lago", "río")),
    ("sand", ("sand", "arena", "playa")),
    ("bridge", ("bridge", "puente")),
    ("marksman", ("marksman", "arquero oscuro", "arqueros oscuros")),
    ("necromancer", ("necromancer", "nigromante")),
    ("demon", ("demon", "demonio", "jefe", "boss")),
    ("mimic", ("mimic", "mímico", "mimico")),
    ("rat", ("rat", "rata")),
    ("barrel", ("barrel", "barril")),
    ("fence", ("fence", "valla")),
    ("bush", ("bush", "arbusto")),
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


# Without a position, each kind gets its own zone of the map, spread from the
# centre outwards, so a village or a battle fills the world instead of a line.
_ZONE_XS = (260, 620, 980, 1340)
_ZONE_YS = (220, 480, 740)
_ZONE_ORDER = ((1, 1), (2, 1), (0, 1), (3, 1), (1, 0), (2, 2), (2, 0), (1, 2), (0, 0), (3, 2), (3, 0), (0, 2))
# One mention of these kinds means a patch of ground, not a single tile.
_PATCHES = {"water": (3, 2), "sand": (3, 2), "path": (6, 1), "road": (6, 1)}
# The agent accepts at most this many objects per answer; never reply with more.
MAX_TOTAL = 30
_PATCH_WORDS = ("lago", "lake", "rio", "río", "river", "playa", "beach", "camino", "calle", "sendero", "carretera")


def _zone(index: int):
    col, row = _ZONE_ORDER[index % len(_ZONE_ORDER)]
    return _ZONE_XS[col], _ZONE_YS[row]


def _grid_positions(kind: str, count: int, centre, cols: int | None = None):
    """count objects of a kind in a compact grid around centre, inside the world."""
    width, height = SIZES.get(kind, (32, 32))
    tile = kind in _PATCHES
    step_x = width if tile else width + 24
    step_y = height if tile else height + 24
    cols = cols or max(1, math.ceil(math.sqrt(count)))
    rows = math.ceil(count / cols)
    left = centre[0] - step_x * (cols - 1) / 2
    top = centre[1] - step_y * (rows - 1) / 2
    for i in range(count):
        x = left + step_x * (i % cols)
        y = top + step_y * (i // cols)
        # Never outside the world: the whole object stays inside the frame.
        yield (min(max(x, width / 2), WORLD_WIDTH - width / 2), min(max(y, height / 2), WORLD_HEIGHT - height / 2))


class SimulatedProvider(AiProvider):
    """Deterministic stand-in for a real model, for demos and tests (no network, no key).

    It understands requests like "3 monedas y una pared en 400 300": one kind per
    part, an optional count and an optional position. Without a position each
    kind is arranged in its own zone of the map (see _zone), and a lake, a river
    or a road becomes a patch of tiles.
    """

    def complete(self, system: str, user: str) -> str:
        request = user.split("Request:", 1)[-1].lower()
        objects = []
        zone = 0
        for part in _parts(request) or [request]:
            kind = _kind_of(part)
            if kind is None:
                continue
            word_at = min(part.find(w) for w in dict(_KINDS)[kind] if w in part)
            count = _count_of(part, word_at)
            position = _position_of(part)
            if position:
                spots = [(min(position[0] + 40 * i, WORLD_WIDTH), position[1]) for i in range(count)]
            else:
                cols = None
                if kind in _PATCHES and count == 1 and any(word in part for word in _PATCH_WORDS):
                    cols, rows = _PATCHES[kind]
                    count = cols * rows
                spots = list(_grid_positions(kind, count, _zone(zone), cols))
                zone += 1
            for x, y in spots[: MAX_TOTAL - len(objects)]:
                objects.append({"id": f"{kind}-{len(objects) + 1}", "kind": kind, "x": x, "y": y})
        if not objects:
            objects.append({"id": "box-1", "kind": "box", "x": WORLD_WIDTH / 2, "y": WORLD_HEIGHT / 2})
        return json.dumps(objects)
