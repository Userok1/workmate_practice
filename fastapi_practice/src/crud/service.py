from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from redis.asyncio import Redis
from datetime import date

from src.crud.models import TradeResultsOrm
from src.crud.schemas import FiltersSchema
from src.crud.utils import cache_load, cache_dump, TradingResultsRepository


async def read_trading_dates(
    days: int | None,
    session_factory: async_sessionmaker[AsyncSession],
    redis_client: Redis,
) -> list[date] | None:
    params = [days]
    cached_data = await cache_load(params, redis_client)
    if cached_data:
        return cached_data
    dates = await TradingResultsRepository.get_trading_dates(days, session_factory)
    if dates:
        await cache_dump(params, list(map(str, dates)), redis_client)
        return dates
    return None


async def read_results(
    filters: FiltersSchema,
    session_factory: async_sessionmaker[AsyncSession],
    redis_client: Redis,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[TradeResultsOrm] | None:
    params = [filters, start_date, end_date]
    cached_data = await cache_load(params, redis_client)
    if cached_data:
        return cached_data
    results: list[TradeResultsOrm] = await TradingResultsRepository.get_results(
        filters, session_factory, start_date, end_date
    )
    if results:
        await cache_dump(params, [result.to_dict() for result in results], redis_client)
        return results
    return None
