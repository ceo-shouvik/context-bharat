"""
Redis client — Upstash serverless Redis for response caching and rate limiting.
Falls back gracefully if Redis is unavailable (non-critical path).
"""
from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client = None


def _get_client():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        from upstash_redis import Redis
        _redis_client = Redis.from_env()
        return _redis_client
    except ImportError:
        try:
            import redis as redis_lib
            _redis_client = redis_lib.from_url(settings.UPSTASH_REDIS_URL)
            return _redis_client
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
            return None


async def get_cached(key: str) -> str | None:
    """Get cached value. Returns None on miss or error."""
    client = _get_client()
    if client is None:
        return None
    try:
        return client.get(key)
    except Exception as e:
        logger.debug(f"Redis get failed for {key}: {e}")
        return None


async def set_cached(key: str, value: str, ttl: int = 300) -> None:
    """Set cached value with TTL (seconds). Silently fails if Redis unavailable."""
    client = _get_client()
    if client is None:
        return
    try:
        client.setex(key, ttl, value)
    except Exception as e:
        logger.debug(f"Redis set failed for {key}: {e}")


async def increment_counter(key: str, ttl: int = 86400) -> int:
    """Increment a counter (for rate limiting). Returns new count."""
    client = _get_client()
    if client is None:
        return 0
    try:
        count = client.incr(key)
        client.expire(key, ttl)
        return count
    except Exception as e:
        logger.debug(f"Redis incr failed for {key}: {e}")
        return 0


async def check_rate_limit(api_key_prefix: str, daily_limit: int) -> tuple[bool, int]:
    """
    Check if an API key is within its daily limit.
    Returns (is_allowed, current_count).
    """
    from datetime import date
    today = date.today().isoformat()
    key = f"ratelimit:{api_key_prefix}:{today}"

    # Check current count BEFORE incrementing to avoid off-by-one
    client = _get_client()
    if client is None:
        return True, 0
    try:
        existing = client.get(key)
        current = int(existing) if existing else 0
        if current >= daily_limit:
            return False, current
    except Exception:
        pass

    count = await increment_counter(key, ttl=86400)
    return count <= daily_limit, count
