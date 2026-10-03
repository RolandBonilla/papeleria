from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.types import Money
from app.models.client import Client

if TYPE_CHECKING:
    from app.models.sale_detail import SaleDetail


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    total: Mapped[Decimal] = mapped_column(Money)

    client: Mapped[Client | None] = relationship()
    details: Mapped[list[SaleDetail]] = relationship(
        back_populates="sale", cascade="all, delete-orphan", order_by="SaleDetail.id"
    )

    @property
    def client_name(self) -> str | None:
        return self.client.name if self.client else None
