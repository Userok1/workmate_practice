import redis.asyncio as redis
import hashlib
import json
from typing import Any
from datetime import datetime

from src.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
)


def hash(params: list[Any]) -> str:
    return hashlib.md5(str(params).encode()).hexdigest()


async def cache_load(
    params: list[Any],
    redis_client: redis.Redis,
) -> list[Any] | None:
    key = hash(params)
    data = await redis_client.get(key)
    if not data:
        return None
    desirialized_data = json.loads(data)
    return desirialized_data


async def cache_dump(
    params: list[Any],
    data: list[Any],
    redis_client: redis.Redis,
) -> None:
    key = hash(params)
    serialized_data = json.dumps(data)
    current_dt_obj = datetime.today()
    try:
        next_dt_obj = datetime(
            current_dt_obj.year,
            current_dt_obj.month,
            current_dt_obj.day + 1,
            hour=14,
            minute=11,
        )
    except ValueError:
        try:
            # Если сегодняшний день - последний день месяца, то месяц увеличивается
            next_dt_obj = datetime(
                current_dt_obj.year,
                current_dt_obj.month + 1,
                1,
                hour=14,
                minute=11,
            )
        except ValueError:
            # Если сегодняшний день - последний день года, то год увеличивается
            next_dt_obj = datetime(
                current_dt_obj.year + 1,
                1,
                1,
                hour=14,
                minute=11,
            )
    ttl = (next_dt_obj - current_dt_obj).seconds
    await redis_client.setex(key, ttl, serialized_data)
    return None
