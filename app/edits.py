"""Requests that remove things from the scene: "borra los enemigos", "elimina todo", "quita las monedas".

Removing is not left to the language model: a fixed set of words decides what goes, so it works
the same with every provider (and with none), never removes the wrong thing because the model
misread the scene, and costs no call to the external API. Whatever the request also asks to add
("borra todo y pon 5 tanques") is handed to the model afterwards, on the scene without the
removed objects.
"""
import re
import unicodedata
from dataclasses import dataclass, field

from .world import (
    ALL_KINDS, CHARACTER_KINDS, ENEMY_KINDS, GROUND_KINDS, REWARD_KINDS, TERRAIN_KINDS,
)

# Verbs that turn a clause into a removal (written without accents: the text is normalised).
_REMOVE_VERBS = (
    "borra", "borrar", "borrame", "borralo", "borralos", "borralas", "elimina", "eliminar", "eliminame",
    "quita", "quitar", "quitame", "saca", "sacar", "limpia", "limpiar", "vacia", "vaciar", "suprime",
    "remove", "delete", "clear", "erase", "wipe",
)
# Words that mean "everything" when nothing more specific is named.
_EVERYTHING = ("todo", "todos", "toda", "todas", "everything", "all", "mapa", "escena", "nivel", "map", "scene", "level")

WEAPON_KINDS = frozenset({
    "sword", "axe", "wand", "bow", "dagger", "hammer", "spear", "staff",
    "pistol", "rifle", "shotgun", "smg", "sniper", "launcher", "grenade",
})
BUILDING_KINDS = frozenset({"wall", "house", "fence", "bunker", "tower", "saloon", "cabin"})
OBSTACLE_KINDS = frozenset({
    "box", "barrel", "spike", "explosive", "sandbag", "barricade", "hedgehog", "rock", "tree", "bush",
    "wagon", "hay", "crates", "trough", "cactus", "lamp",
})

# Groups people name in a request -> kinds. The first words that match win for that span of text.
_GROUPS = (
    (("enemigo", "enemigos", "enemy", "enemies", "monstruo", "monstruos", "monster", "monsters", "malos"), ENEMY_KINDS),
    (("objeto", "objetos", "item", "items", "recompensa", "recompensas", "coleccionable", "coleccionables"),
     REWARD_KINDS | {"coin"}),
    (("arma", "armas", "weapon", "weapons", "pistolas", "fusiles"), WEAPON_KINDS),
    (("moneda", "monedas", "coin", "coins"), frozenset({"coin"})),
    (("personaje", "personajes", "aldeanos", "npc", "npcs", "character", "characters", "aliados", "allies"),
     CHARACTER_KINDS),
    (("obstaculo", "obstaculos", "obstacle", "obstacles", "trampa", "trampas"), OBSTACLE_KINDS),
    (("edificio", "edificios", "construccion", "construcciones", "building", "buildings"), BUILDING_KINDS),
    (("terreno", "suelo", "terrain", "ground", "caminos", "carreteras"), GROUND_KINDS | TERRAIN_KINDS),
    (("soldado", "soldados", "soldier", "soldiers", "ejercito", "army"),
     frozenset({"soldier", "grenadier", "legionary", "captain"})),
    (("jugador", "player", "heroe", "hero"), frozenset({"player"})),
)

# Single kinds by name, Spanish and English (singular; plurals are matched by the pattern).
_KIND_WORDS = {
    "box": ("caja", "box"), "wall": ("pared", "muro", "wall"), "house": ("casa", "house"),
    "tree": ("arbol", "tree"), "spike": ("pincho", "spike"), "enemy": ("slime",),
    "villager": ("aldeano", "aldeana", "villager"), "knight": ("caballero", "knight"), "wizard": ("mago", "wizard"),
    "bat": ("murcielago", "bat"), "spider": ("arana", "spider"), "ghost": ("fantasma", "ghost"),
    "brute": ("ogro", "brute"), "chest": ("cofre", "chest"), "potion": ("pocion", "potion"),
    "sword": ("espada", "sword"), "axe": ("hacha", "axe"), "wand": ("varita", "wand"), "bow": ("arco", "bow"),
    "barrel": ("barril", "barrel"), "fence": ("valla", "fence"), "bush": ("arbusto", "bush"),
    "dagger": ("daga", "dagger"), "hammer": ("martillo", "hammer"), "spear": ("lanza", "spear"),
    "staff": ("baculo", "baston", "staff"), "path": ("camino", "path"), "water": ("agua", "water"),
    "sand": ("arena", "sand"), "bridge": ("puente", "bridge"), "marksman": ("arquero oscuro", "marksman"),
    "necromancer": ("nigromante", "necromancer"), "demon": ("demonio", "demon", "jefe", "boss"),
    "mimic": ("mimico", "mimic"), "rat": ("rata", "rat"), "soldier": ("fusilero",),
    "grenadier": ("granadero", "grenadier"), "tank": ("tanque", "tank"), "artillery": ("artilleria", "canon", "artillery"),
    "ally": ("soldado aliado",), "guard": ("guardia", "guard"), "sandbag": ("saco", "sacos terreros", "sandbag"),
    "barricade": ("barricada", "barricade"), "hedgehog": ("erizo", "hedgehog"), "bunker": ("bunker",),
    "tower": ("torre", "tower"), "flag": ("bandera", "flag"), "banner": ("estandarte", "banner"),
    "rock": ("colina", "roca", "rock"), "road": ("carretera", "road"), "medkit": ("botiquin", "medkit"),
    "legionary": ("legionario", "legionary"), "captain": ("capitan", "captain"),
    "pistol": ("pistola", "pistol"), "rifle": ("fusil", "rifle"), "shotgun": ("escopeta", "shotgun"),
    "smg": ("subfusil", "metralleta", "smg"), "sniper": ("francotirador", "sniper"),
    "launcher": ("lanzacohetes", "bazooka", "launcher"), "grenade": ("granada", "grenade"),
    "explosive": ("barril explosivo", "barriles explosivos", "explosivo", "explosive"), "coin": ("moneda", "coin"),
    "saloon": ("saloon", "cantina"), "cabin": ("cabana", "cabin"), "wagon": ("carreta", "carro", "wagon"),
    "hay": ("fardo", "heno", "paja", "hay"), "crates": ("pila de cajas", "cajas apiladas", "crates"),
    "trough": ("abrevadero", "trough"), "cactus": ("cactus", "saguaro"), "lamp": ("farol", "farola", "lamp"),
    "boardwalk": ("pasarela", "tablones", "boardwalk"), "dirt": ("tierra", "dirt"),
    "bandit": ("bandido", "pistolero", "forajido", "bandit", "outlaw"),
}

_CLAUSE_SPLIT = re.compile(r"\s*(?:[,;.]|\by luego\b|\by despues\b|\bluego\b|\bdespues\b|\bthen\b|\band\b|\by\b|\be\b)\s*")


def normalise(text: str) -> str:
    """Lower case, no accents, single spaces: 'Elimína  TODO' -> 'elimina todo'."""
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def _has_word(text: str, word: str) -> bool:
    """The word (or phrase) with an optional plural ending, as whole words."""
    return re.search(rf"\b{re.escape(word)}(?:s|es)?\b", text) is not None


def _is_removal(clause: str) -> bool:
    return any(re.search(rf"\b{verb}\b", clause) for verb in _REMOVE_VERBS)


def _targets(clause: str) -> set:
    """Kinds a removal clause names; 'everything' (no player) when it names none but says 'todo'/'mapa'."""
    kinds = set()
    rest = clause
    # Longer phrases first ("barril explosivo" before "barril", "soldado aliado" before "soldado").
    phrases = [(word, frozenset({kind})) for kind, words in _KIND_WORDS.items() for word in words]
    phrases += [(word, group) for words, group in _GROUPS for word in words]
    for word, group in sorted(phrases, key=lambda item: -len(item[0])):
        if _has_word(rest, word):
            kinds |= set(group)
            rest = re.sub(rf"\b{re.escape(word)}(?:s|es)?\b", " ", rest)
    if kinds:
        return kinds
    if any(_has_word(clause, word) for word in _EVERYTHING) or re.search(r"\b(limpia|limpiar|vacia|vaciar|clear|wipe)\b", clause):
        return set(ALL_KINDS) - {"player"}
    return set()


@dataclass
class Edit:
    """What a request removes and what it still asks to add."""

    remove_kinds: set = field(default_factory=set)
    add_request: str = ""

    @property
    def removes(self) -> bool:
        return bool(self.remove_kinds)


def parse_edit(request: str) -> Edit:
    """Split a request into removals (decided here) and the part that asks to add things."""
    text = normalise(request)
    if not _is_removal(text):
        return Edit(add_request=request.strip())
    remove, keep = set(), []
    for clause in filter(None, _CLAUSE_SPLIT.split(text)):
        if _is_removal(clause):
            remove |= _targets(clause)
        else:
            keep.append(clause)
    # A clause without a verb right after a removal ("borra los enemigos y las monedas") still removes.
    if remove and keep:
        leftover = []
        for clause in keep:
            named = _targets(f"borra {clause}") if not _asks_to_add(clause) else set()
            if named and named != set(ALL_KINDS) - {"player"}:
                remove |= named
            else:
                leftover.append(clause)
        keep = leftover
    return Edit(remove_kinds=remove, add_request=" y ".join(keep).strip())


_ADD_VERBS = ("pon", "poner", "ponme", "anade", "agrega", "crea", "crear", "coloca", "genera", "mete", "haz",
              "add", "create", "place", "put", "spawn", "make", "build")


def _asks_to_add(clause: str) -> bool:
    return any(re.search(rf"\b{verb}\b", clause) for verb in _ADD_VERBS) or bool(re.search(r"\d", clause))


def removed_ids(scene: list, kinds: set) -> list:
    """Ids of the scene objects whose kind is in `kinds`, in scene order."""
    return [obj["id"] for obj in scene if obj.get("kind") in kinds]
