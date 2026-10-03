from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.sale import Sale


class SaleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, sale_id: int) -> Sale | None:
        return self.db.get(Sale, sale_id)

    def add(self, sale: Sale) -> Sale:
        self.db.add(sale)
        self.db.flush()
        return sale

    def list(self, date_from: datetime | None = None, date_to: datetime | None = None) -> list[Sale]:
        """Lista ventas, de la más reciente a la más antigua. ``date_to`` es exclusivo."""
        stmt = select(Sale).options(selectinload(Sale.details)).order_by(Sale.date.desc(), Sale.id.desc())
        if date_from:
            stmt = stmt.where(Sale.date >= date_from)
        if date_to:
            stmt = stmt.where(Sale.date < date_to)
        return list(self.db.scalars(stmt))
