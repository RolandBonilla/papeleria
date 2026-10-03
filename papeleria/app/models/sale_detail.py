from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import Money
from app.models.product import Product
from app.models.sale import Sale


class SaleDetail(Base):
    __tablename__ = "sale_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Money)
    subtotal: Mapped[Decimal] = mapped_column(Money)

    sale: Mapped[Sale] = relationship(back_populates="details")
    product: Mapped[Product] = relationship()

    @property
    def product_name(self) -> str:
        return self.product.name
