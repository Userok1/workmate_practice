from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from redis.asyncio import Redis
from datetime import date

from src.crud.models import TradeResultsOrm
from src.crud.schemas import FiltersSchema
from src.crud.utils import cache_load, cache_dump


async def get_trading_dates(
    days: int | None,
    session_factory: async_sessionmaker[AsyncSession],
    redis_client: Redis,
) -> list[date]:
    params = [days]
    cached_data = await cache_load(params, redis_client)
    if cached_data:
        return cached_data
    else:
        async with session_factory() as session:
            async with session.begin():
                dates_select_stmt = (
                    select(TradeResultsOrm.date)
                    .group_by(TradeResultsOrm.date)
                    .limit(days)
                    .order_by(TradeResultsOrm.date.desc())
                )
                dates = list((await session.scalars(dates_select_stmt)).all())
                await cache_dump(params, list(map(str, dates)), redis_client)
                return dates


async def get_results(
    filters: FiltersSchema,
    session_factory: async_sessionmaker[AsyncSession],
    redis_client: Redis,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[TradeResultsOrm]:
    filters_apply = []
    params = [filters, start_date, end_date]
    cached_data = await cache_load(params, redis_client)
    if cached_data:
        return cached_data
    else:
        async with session_factory() as session:
            async with session.begin():
                if filters.oil_id:
                    filters_apply.append(and_(TradeResultsOrm.oil_id == filters.oil_id))
                if filters.delivery_type_id:
                    filters_apply.append(
                        and_(
                            TradeResultsOrm.delivery_type_id == filters.delivery_type_id
                        )
                    )
                if filters.delivery_basis_id:
                    filters_apply.append(
                        and_(
                            TradeResultsOrm.delivery_basis_id
                            == filters.delivery_basis_id
                        )
                    )

                page = filters.page
                page_size = filters.page_size
                if start_date and end_date:
                    trading_results_select_stmt = select(TradeResultsOrm).where(
                        and_(
                            *filters_apply,
                            TradeResultsOrm.date.between(start_date, end_date),
                        )
                    )
                else:
                    trading_results_select_stmt = select(TradeResultsOrm).where(
                        *filters_apply
                    )
                trading_results_select_stmt = (
                    trading_results_select_stmt.limit(page_size)
                    .offset((page - 1) * page_size)
                    .order_by(TradeResultsOrm.date.desc())
                )

                results = list(
                    (await session.scalars(trading_results_select_stmt)).all()
                )
                await cache_dump(
                    params, [result.to_dict() for result in results], redis_client
                )
                return results
