"""Inventario: ingresos, descuentos de stock y alertas (patrón Observer)."""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.exceptions import InsufficientStockError, InvalidDataError, NotFoundError
from app.models.alert import Alert
from app.models.product import STATUS_AVAILABLE, STATUS_LOW, STATUS_OUT, Product
from app.models.stock_movement import MOVEMENT_ENTRY, StockMovement
from app.patterns.observer import Observer, Subject
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository

STATUSES = (STATUS_AVAILABLE, STATUS_LOW, STATUS_OUT)


@dataclass
class StockChangedEvent:
    db: Session
    product: Product


class LowStockAlertObserver(Observer):
    """Genera una alerta cuando stock <= stock mínimo y la cierra cuando el stock se recupera."""

    def update(self, event: StockChangedEvent) -> None:
        repository = InventoryRepository(event.db)
        product = event.product
        open_alert = repository.get_open_alert(product.id)

        if product.active and product.is_low_stock:
            message = self._message(product)
            if open_alert is None:
                repository.add_alert(Alert(product_id=product.id, message=message))
            else:
                open_alert.message = message
        elif open_alert is not None:
            open_alert.resolved = True

    @staticmethod
    def _message(product: Product) -> str:
        prefix = "Sin stock" if product.stock == 0 else "Stock bajo"
        return f"{prefix}: {product.name} ({product.code}) tiene {product.stock} unidades, mínimo {product.min_stock}."


stock_subject = Subject()
stock_subject.attach(LowStockAlertObserver())


class InventoryService:
    def __init__(self, db: Session, subject: Subject = stock_subject) -> None:
        self.db = db
        self.subject = subject
        self.products = ProductRepository(db)
        self.repository = InventoryRepository(db)

    def notify_stock_changed(self, product: Product) -> None:
        self.subject.notify(StockChangedEvent(self.db, product))

    def apply_movement(self, product: Product, delta: int, movement_type: str,
                       reference: str | None = None, user_id: int | None = None) -> None:
        """Cambia el stock, registra el movimiento y avisa a los observadores. No hace commit."""
        new_stock = product.stock + delta
        if new_stock < 0:
            raise InsufficientStockError(
                f"Stock insuficiente de {product.name}: disponible {product.stock}, solicitado {-delta}"
            )
        product.stock = new_stock
        self.repository.add_movement(StockMovement(
            product_id=product.id, type=movement_type, quantity=delta,
            reference=reference, user_id=user_id,
        ))
        self.notify_stock_changed(product)

    def register_entry(self, product_id: int, quantity: int, note: str | None = None,
                       user_id: int | None = None) -> Product:
        """RF-04: ingreso de mercadería."""
        if quantity <= 0:
            raise InvalidDataError("La cantidad ingresada debe ser mayor que cero")
        product = self.products.get(product_id)
        if product is None or not product.active:
            raise NotFoundError("Producto no encontrado")
        self.apply_movement(product, quantity, MOVEMENT_ENTRY, reference=note, user_id=user_id)
        self.db.commit()
        return product

    def list_inventory(self, status: str | None = None) -> list[Product]:
        products = self.products.search()
        if status:
            products = [p for p in products if p.stock_status == status]
        return products

    def low_stock_products(self) -> list[Product]:
        return self.products.list_low_stock()

    def open_alerts(self) -> list[Alert]:
        return self.repository.list_open_alerts()
