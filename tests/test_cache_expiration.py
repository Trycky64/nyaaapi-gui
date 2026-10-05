from nyaaapi_gui.services.cache import MemoryCache


def test_memory_cache_expires_and_evicts_lru(monkeypatch) -> None:
    import nyaaapi_gui.services.cache as cache_module

    now = 100.0
    monkeypatch.setattr(cache_module, "monotonic", lambda: now)
    cache = MemoryCache[str](max_items=1, ttl_seconds=5)
    cache.set("a", "first")
    assert cache.get("a") == "first"
    cache.set("b", "second")
    assert cache.get("a") is None
    assert cache.get("b") == "second"
    now += 6
    assert cache.get("b") is None
