from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.product import Product
from app.models.stock_movement import StockMovement


class InventoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_movement(self, movement: StockMovement) -> StockMovement:
        self.db.add(movement)
        return movement

    def get_open_alert(self, product_id: int) -> Alert | None:
        stmt = select(Alert).where(Alert.product_id == product_id, Alert.resolved.is_(False))
        return self.db.scalar(stmt)

    def add_alert(self, alert: Alert) -> Alert:
        self.db.add(alert)
        self.db.flush()
        return alert

    def list_open_alerts(self) -> list[Alert]:
        stmt = (
            select(Alert)
            .join(Product, Alert.product_id == Product.id)
            .where(Alert.resolved.is_(False), Product.active.is_(True))
            .order_by(Alert.created_at.desc(), Alert.id.desc())
        )
        return list(self.db.scalars(stmt))
