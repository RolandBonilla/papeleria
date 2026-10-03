from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import Money
from app.models.category import Category

STATUS_AVAILABLE = "Disponible"
STATUS_LOW = "Stock bajo"
STATUS_OUT = "Sin stock"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    price: Mapped[Decimal] = mapped_column(Money)
    stock: Mapped[int] = mapped_column(default=0)
    min_stock: Mapped[int] = mapped_column(default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped[Category] = relationship()

    @property
    def category_name(self) -> str:
        return self.category.name

    @property
    def is_low_stock(self) -> bool:
        return self.stock <= self.min_stock

    @property
    def stock_status(self) -> str:
        if self.stock == 0:
            return STATUS_OUT
        if self.is_low_stock:
            return STATUS_LOW
        return STATUS_AVAILABLE
