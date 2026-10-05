from __future__ import annotations

from collections import OrderedDict
from time import monotonic
from typing import Generic, TypeVar

T = TypeVar("T")


class MemoryCache(Generic[T]):
    """Small bounded TTL cache for immutable service values."""

    def __init__(self, *, max_items: int = 128, ttl_seconds: float = 300.0) -> None:
        self.max_items = max_items
        self.ttl_seconds = ttl_seconds
        self._items: OrderedDict[object, tuple[float, T]] = OrderedDict()

    def get(self, key: object) -> T | None:
        """Return an unexpired cached value, or None when absent."""
        value = self._items.get(key)
        if value is None:
            return None
        created, result = value
        if monotonic() - created > self.ttl_seconds:
            del self._items[key]
            return None
        self._items.move_to_end(key)
        return result

    def set(self, key: object, value: T) -> None:
        """Insert a value and discard least-recently-used entries if needed."""
        self._items[key] = (monotonic(), value)
        self._items.move_to_end(key)
        while len(self._items) > self.max_items:
            self._items.popitem(last=False)

    def clear(self) -> None:
        """Remove all cached values."""
        self._items.clear()
