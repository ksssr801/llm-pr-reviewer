import redis.asyncio as redis
from app.config import get_settings
from app.logger_config import get_logger

logger = get_logger(__name__)

redis_client: redis.Redis | None = None


async def init_redis():
    global redis_client
    settings = get_settings()
    redis_client = redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )
    logger.info("Redis connection initialized")


def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis client not initialized")
    return redis_client
