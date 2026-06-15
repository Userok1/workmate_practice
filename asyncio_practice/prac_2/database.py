import os
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from datetime import date as DatetimeDate
from typing import AsyncGenerator
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH, override=True)

DB_DBMS=os.getenv("DB_DBMS", "postgresql+asyncpg")
DB_USER=os.getenv("DB_USER", "postgres")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST", "localhost")
DB_PORT=os.getenv("DB_PORT", "5432")
DB_NAME=os.getenv("DB_NAME")
POSTGRES_URL = f"{DB_DBMS}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD is not set in environment variables")
if not DB_NAME:
    raise ValueError("DB_NAME is not set in environment variables")

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
