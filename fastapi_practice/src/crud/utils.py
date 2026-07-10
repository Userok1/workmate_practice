import redis.asyncio as redis
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from datetime import date
import hashlib
import json
from typing import Any
from datetime import datetime

from src.config import settings
from src.crud.schemas import FiltersSchema
from src.crud.models import TradeResultsOrm

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
    # await redis_client.setex(key, ttl, serialized_data)
    await redis_client.set(key, serialized_data, ttl)
    return None


class TradingResultsRepository:
    @classmethod
    async def get_results(
        cls,
        filters: FiltersSchema,
        session_factory: async_sessionmaker[AsyncSession],
        start_date: date | None = None,
        end_date: date | None = None,
    ):
        filters_apply = []
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

                return results

    @classmethod
    async def get_trading_dates(
        cls, days: int | None, session_factory: async_sessionmaker[AsyncSession]
    ):
        async with session_factory() as session:
            async with session.begin():
                dates_select_stmt = (
                    select(TradeResultsOrm.date)
                    .group_by(TradeResultsOrm.date)
                    .limit(days)
                    .order_by(TradeResultsOrm.date.desc())
                )
                dates = list((await session.scalars(dates_select_stmt)).all())
                return dates
