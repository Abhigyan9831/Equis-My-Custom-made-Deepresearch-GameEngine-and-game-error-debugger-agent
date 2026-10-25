
import hashlib
import json
from upstash_redis import Redis
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

_redis: Redis | None = None

def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis(
            url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN,)
    return _redis


def make_cache_key(text: str, prefix: str = "log") -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"ged:v1:{prefix}:{digest}"


def get_cached(key: str) -> dict | None:
    try:
        data = get_redis().get(key)
        if data:
            logger.info("Cache hit", extra={"key": key[:40]})
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Cache get failed: {e}")
    return None


def set_cached(key: str, value: dict) -> None:
    try:
        get_redis().setex(key, settings.CACHE_TTL_SECONDS, json.dumps(value))
        logger.info("Cache set", extra={"ttl": settings.CACHE_TTL_SECONDS})
    except Exception as e:
        logger.warning(f"Cache set failed: {e}")

