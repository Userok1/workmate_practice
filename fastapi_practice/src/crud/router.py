from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from redis.asyncio import Redis
from datetime import date
from typing import Annotated

from src.crud.models import TradeResultsOrm
from src.database import get_async_db_session
from src.crud.schemas import (
    DatesReturnSchema,
    FiltersSchema,
    TradingResultsReturnSchema,
)
from src.crud.service import get_trading_dates, get_results
from src.crud.dependencies import get_redis_client

router = APIRouter()


@router.get("/trades/dates", response_model=DatesReturnSchema)
async def get_last_trading_dates(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_db_session)
    ],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    days: int | None = None,
):
    dates: list[date] | None = await get_trading_dates(
        days, session_factory, redis_client
    )
    if not dates:
        raise HTTPException(
            status_code=404,
            detail="Trade results dates not found",
        )
    return {"dates": dates}


@router.get(
    "/trades/{start_date}/{end_date}", response_model=TradingResultsReturnSchema
)
async def get_dynamics(
    filters: Annotated[FiltersSchema, Query()],
    start_date: Annotated[date, Path(description="Example 2026-01-01")],
    end_date: Annotated[date, Path(description="Example 2026-12-31")],
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_db_session)
    ],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
):
    trade_results: list[TradeResultsOrm] = await get_results(
        filters,
        session_factory,
        redis_client,
        start_date,
        end_date,
    )
    if not trade_results:
        raise HTTPException(
            status_code=404,
            detail="Trade results not found",
        )
    return {
        "page": filters.page,
        "page_size": filters.page_size,
        "total": len(trade_results),
        "trade_results": trade_results,
    }


@router.get("/trades", response_model=TradingResultsReturnSchema)
async def get_trading_results(
    filters: Annotated[FiltersSchema, Query()],
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_async_db_session)
    ],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
):
    trade_results: list[TradeResultsOrm] = await get_results(
        filters, session_factory, redis_client
    )
    if not trade_results:
        raise HTTPException(status_code=404, detail="Trading results not found")

    return {
        "page": filters.page,
        "page_size": filters.page_size,
        "total": len(trade_results),
        "trade_results": trade_results,
    }
