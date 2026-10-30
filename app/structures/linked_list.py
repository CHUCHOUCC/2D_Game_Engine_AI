from .node import Node


class LinkedList:
    """Singly linked list with a head and a tail reference.

    Invariant: _head and _tail are both None (empty) or both point into the same
    chain, _tail.next is None, and _size counts the nodes of the chain.
    Costs: add and add_first are O(1) thanks to the tail; find and remove are O(n).
    """

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def size(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def add(self, data) -> None:
        """Add an element at the end."""
        node = Node(data)
        if self._tail is None:
            self._head = node
        else:
            self._tail.next = node
        self._tail = node
        self._size += 1

    def add_first(self, data) -> None:
        """Add an element at the start."""
        self._head = Node(data, self._head)
        if self._tail is None:
            self._tail = self._head
        self._size += 1

    def find(self, predicate):
        """The first element that satisfies the condition, or None."""
        current = self._head
        while current is not None:
            if predicate(current.data):
                return current.data
            current = current.next
        return None

    def remove(self, predicate) -> bool:
        """Remove the first element that satisfies the condition; True if one was removed."""
        previous = None
        current = self._head
        while current is not None:
            if predicate(current.data):
                if previous is None:
                    self._head = current.next
                else:
                    previous.next = current.next
                if current is self._tail:
                    self._tail = previous
                self._size -= 1
                return True
            previous = current
            current = current.next
        return False

    def clear(self) -> None:
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        current = self._head
        while current is not None:
            yield current.data
            current = current.next
