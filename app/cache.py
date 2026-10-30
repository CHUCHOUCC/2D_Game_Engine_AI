"""Cache of generated objects.

The same prompt on the same scene gives the same objects, so the answer is kept for a while: a
repeated request skips the external AI API (time and money) and the physics pass. The key covers
everything that changes the answer: provider and model, the prompt (trimmed, lower case, single
spaces) and the scene (canonical JSON). Errors are never cached.
"""
import copy
import hashlib
import json
import os

from .lru_cache import LRUCache

generation_cache = LRUCache(
    capacity=int(os.environ.get("AI_CACHE_SIZE", "256")),
    ttl_seconds=int(os.environ.get("AI_CACHE_TTL", "1800")),
)


def provider_id(provider) -> str:
    """Name of the provider plus its model, so two models never share answers."""
    return f"{type(provider).__name__}:{getattr(provider, 'model', '')}"


def generation_key(provider, prompt: str, scene: list) -> str:
    normalized = " ".join(prompt.lower().split())
    canonical_scene = json.dumps(scene, sort_keys=True, separators=(",", ":"))
    raw = "\n".join((provider_id(provider), normalized, canonical_scene))
    return hashlib.sha256(raw.encode()).hexdigest()


def cached_generation(provider, prompt: str, scene: list, generate):
    """(objects, hit): the cached objects or those of generate(), stored for next time."""
    key = generation_key(provider, prompt, scene)
    found = generation_cache.get(key)
    if found is not None:
        return copy.deepcopy(found), True
    objects = generate()
    generation_cache.put(key, copy.deepcopy(objects))
    return objects, False
