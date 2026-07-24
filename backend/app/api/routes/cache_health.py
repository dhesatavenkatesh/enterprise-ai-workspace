from fastapi import APIRouter

from app.cache.redis_cache import redis_cache

router = APIRouter(
    prefix="/api/cache",
    tags=["Cache"],
)


@router.get(
    "/health",
    summary="Check Redis cache health",
)
def cache_health() -> dict[str, object]:
    connected = redis_cache.ping()

    return {
        "status": "healthy" if connected else "unavailable",
        "redis_connected": connected,
    }


@router.get(
    "/test",
    summary="Test Redis cache read and write",
)
def test_cache() -> dict[str, object]:
    test_key = "enterprise_ai:test"

    write_success = redis_cache.set(
        key=test_key,
        value={
            "message": "Redis cache is working",
        },
        expire_seconds=60,
    )

    cached_value = redis_cache.get(test_key)

    return {
        "write_success": write_success,
        "cached_value": cached_value,
        "ttl": redis_cache.ttl(test_key),
    }