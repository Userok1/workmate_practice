from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from datetime import date as DatetimeDate

SQLITE_URL = "sqlite+pysqlite:///spimex_trading_results.db"


engine = create_engine(
    SQLITE_URL, connect_args={"check_same_thread": False}
)

session_factory = sessionmaker(engine, autoflush=False, expire_on_commit=False)


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
