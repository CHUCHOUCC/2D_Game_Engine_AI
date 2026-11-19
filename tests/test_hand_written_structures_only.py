"""The navigation code must use our own structures, not the ones that come with Python."""
import re
from pathlib import Path

NAVIGATION = Path(__file__).resolve().parents[1] / "app" / "navigation"
STRUCTURES = Path(__file__).resolve().parents[1] / "app" / "structures"
FORBIDDEN = re.compile(r"\b(from collections import .*deque|import deque|import queue|from queue import|import heapq|from heapq import)\b")


def test_navigation_does_not_import_native_queues():
    for path in NAVIGATION.glob("*.py"):
        assert not FORBIDDEN.search(path.read_text()), f"{path.name} imports a native queue"


def test_our_structures_do_not_use_native_containers_to_store_elements():
    for path in STRUCTURES.glob("*.py"):
        source = path.read_text()
        assert not FORBIDDEN.search(source), f"{path.name} imports a native queue"
        assert not re.search(r"= \[\]|= list\(|= dict\(|= \{\}", source), f"{path.name} stores elements in a native container"
