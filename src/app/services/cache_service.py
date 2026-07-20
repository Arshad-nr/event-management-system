import json
import logging

logger = logging.getLogger(__name__)

EVENTS_CACHE_PREFIX = "events:list:"
CACHE_TTL = 300

async def get_cached_events(redis, cache_key: str) -> dict | None:
    try:
        data = await redis.get(cache_key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.error(f"Redis get error: {e}")
    return None

async def set_cached_events(redis, cache_key: str, data: dict) -> None:
    try:
        await redis.set(cache_key, json.dumps(data), ex=CACHE_TTL)
    except Exception as e:
        logger.error(f"Redis set error: {e}")

async def invalidate_events_cache(redis) -> None:
    try:
        keys = await redis.keys(f"{EVENTS_CACHE_PREFIX}*")
        if keys:
            await redis.delete(*keys)
    except Exception as e:
        logger.error(f"Redis invalidate error: {e}")
