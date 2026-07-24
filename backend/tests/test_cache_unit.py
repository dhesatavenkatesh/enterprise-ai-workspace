from unittest.mock import MagicMock

from app.cache.redis_cache import RedisCache


def test_cache_set_and_get(monkeypatch):
    cache = RedisCache()
    fake_client = MagicMock()
    fake_client.setex.return_value = True
    fake_client.get.return_value = '{"status": "working"}'
    cache.client = fake_client

    assert cache.set("test:key", {"status": "working"}, 60) is True
    assert cache.get("test:key") == {"status": "working"}
