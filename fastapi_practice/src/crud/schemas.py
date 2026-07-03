from pydantic import BaseModel, Field
from datetime import date as DatetimeDate


class Base(BaseModel):
    pass


class DatesReturnSchema(Base):
    dates: list[DatetimeDate]

    model_config = {"from_attributes": True}


class FiltersSchema(Base):
    oil_id: str | None = None
    delivery_type_id: str | None = None
    delivery_basis_id: str | None = None
    page: int = 1
    page_size: int = Field(default=100, gt=0, le=500)


class TradingResultReturnSchema(Base):
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: int | None = None
    total: int | None = None
    count: int | None = None
    date: DatetimeDate
    created_on: DatetimeDate
    updated_on: DatetimeDate | None = None

    model_config = {"from_attributes": True}


class TradingResultsReturnSchema(Base):
    page: int
    page_size: int
    total: int
    trade_results: list[TradingResultReturnSchema]
