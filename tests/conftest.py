import pytest


@pytest.fixture(autouse=True)
def fresh_generation_cache():
    """Every test starts with an empty cache of generated objects."""
    from app.cache import generation_cache

    generation_cache.clear()
    yield
    generation_cache.clear()
