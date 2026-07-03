from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date as DatetimeDate
from typing import Any

from src.database import Base


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
    created_on: Mapped[DatetimeDate] = mapped_column(default=func.current_date())
    updated_on: Mapped[DatetimeDate | None] = mapped_column(default=None)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "exchange_product_id": self.exchange_product_id,
            "exchange_product_name": self.exchange_product_name,
            "oil_id": self.oil_id,
            "delivery_basis_id": self.delivery_basis_id,
            "delivery_basis_name": self.delivery_basis_name,
            "delivery_type_id": self.delivery_type_id,
            "volume": self.volume,
            "total": self.total,
            "count": self.count,
            "date": self.date.isoformat(),
            "created_on": self.created_on.isoformat(),
            "updated_on": self.updated_on.isoformat() if self.updated_on else None,
        }
        return data
