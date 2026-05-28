import os
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import date as DatetimeDate
from typing import AsyncGenerator

POSTGRES_URL = os.getenv("DATABASE_URL")


async def get_async_db_session() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(POSTGRES_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False, class_=AsyncSession)

    yield session_factory

    await engine.dispose()


class Base(DeclarativeBase):
    pass


class TradeResultsOrm(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_product_id: Mapped[str]
    exchange_product_name: Mapped[str]
    oil_id: Mapped[str]
    delivery_basis_id: Mapped[str]
    delivery_basis_name: Mapped[str]
    delivery_type_id: Mapped[str]
    volume: Mapped[int | None]
    total: Mapped[int | None]
    count: Mapped[int | None]
    date: Mapped[DatetimeDate]
    create_on: Mapped[DatetimeDate] = mapped_column(default=func.current_date())
    updated_on: Mapped[DatetimeDate | None] = mapped_column(default=None)
