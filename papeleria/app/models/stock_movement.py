from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

MOVEMENT_INITIAL = "INICIAL"
MOVEMENT_ENTRY = "INGRESO"
MOVEMENT_SALE = "VENTA"


class StockMovement(Base):
    """Historial de cambios de stock. ``quantity`` es positiva al ingresar y negativa al vender."""

    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[int]
    reference: Mapped[str | None] = mapped_column(String(100))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
