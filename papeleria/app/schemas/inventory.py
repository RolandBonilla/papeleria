from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StockEntryCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    note: str | None = Field(default=None, max_length=100)


class InventoryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    category_name: str
    stock: int
    min_stock: int
    stock_status: str


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    message: str
    created_at: datetime
    resolved: bool
