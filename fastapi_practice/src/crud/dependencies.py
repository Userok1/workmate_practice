import redis.asyncio as redis
from src.crud.utils import redis_client


async def get_redis_client() -> redis.Redis:
    return redis_client
