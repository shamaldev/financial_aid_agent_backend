# app/redis_client.py
import os
import aioredis
from dotenv import load_dotenv
from utils.log_utils.logger_instances import app_logger

load_dotenv()                   # so REDIS_URL comes from your .env
# only the URL itself as the default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app_logger.log(f"Connecting to Redis at {REDIS_URL}")

redis: aioredis.Redis | None = None



async def init_redis_pool() -> None:
    """
    Call in FastAPI startup event to initialize the global pool.
    """
    app_logger.log('Started')

    global redis
    redis = await aioredis.from_url(
        REDIS_URL, encoding="utf-8", decode_responses=True
    )

async def close_redis_pool() -> None:
    """
    Call in FastAPI shutdown event to cleanly close the pool.
    """

    if redis is not None:
        app_logger.log('Started')

        await redis.close()

async def get_redis() -> aioredis.Redis:
    """
    FastAPI dependency for pulling in the existing pool.
    """
    app_logger.log('Started')

    if redis is None:
        app_logger.log('Failed', level='error')
        raise RuntimeError("Redis pool not initialized")
    return redis
