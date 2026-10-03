from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class SaleCreate(BaseModel):
    client_id: int | None = None
    items: list[SaleItemCreate] = Field(min_length=1)


class SaleDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
    client_id: int | None
    client_name: str | None
    total: Decimal
    details: list[SaleDetailOut]


class SalesReportOut(BaseModel):
    sales: list[SaleOut]
    count: int
    total: Decimal


class DashboardOut(BaseModel):
    total_products: int
    low_stock_products: int
    sales_today: int
    total_sold_today: Decimal
