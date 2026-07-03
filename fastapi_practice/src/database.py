from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from src.config import settings

engine = create_async_engine(url=settings.DB_DSN)


class Base(DeclarativeBase):
    pass


async def get_async_db_session() -> AsyncGenerator[
    async_sessionmaker[AsyncSession], None
]:
    # async with engine.begin() as conn:
    # await conn.run_sync(Base.metadata.drop_all)
    # await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, autoflush=False, class_=AsyncSession
    )

    yield session_factory

    await engine.dispose()
