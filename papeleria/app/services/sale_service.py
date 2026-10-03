"""Ventas. Las funciones de cálculo son puras (sin base de datos) para probarlas de forma aislada."""
from collections import defaultdict
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Iterable

from sqlalchemy.orm import Session

from app.exceptions import InsufficientStockError, InvalidDataError, NotFoundError
from app.models.sale import Sale
from app.models.sale_detail import SaleDetail
from app.models.stock_movement import MOVEMENT_SALE
from app.repositories.client_repository import ClientRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.schemas.sale import SaleCreate
from app.services.inventory_service import InventoryService

CENT = Decimal("0.01")


def calculate_subtotal(unit_price, quantity: int) -> Decimal:
    """RF-06: subtotal = precio unitario x cantidad, redondeado a centavos."""
    try:
        price = Decimal(str(unit_price))
    except InvalidOperation:
        raise InvalidDataError("El precio unitario no es un número válido") from None
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise InvalidDataError("La cantidad debe ser un número entero")
    if price <= 0:
        raise InvalidDataError("El precio unitario debe ser mayor que cero")
    if quantity <= 0:
        raise InvalidDataError("La cantidad debe ser mayor que cero")
    return (price * quantity).quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_total(items: Iterable[tuple]) -> Decimal:
    """Suma los subtotales de una lista de pares (precio unitario, cantidad)."""
    subtotals = [calculate_subtotal(price, quantity) for price, quantity in items]
    if not subtotals:
        raise InvalidDataError("La venta debe tener al menos un producto")
    return sum(subtotals, Decimal("0.00"))


class SaleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sales = SaleRepository(db)
        self.products = ProductRepository(db)
        self.clients = ClientRepository(db)
        self.inventory = InventoryService(db)

    def create_sale(self, data: SaleCreate, user_id: int | None = None) -> Sale:
        """RF-05, RF-06 y RF-07: registra la venta, calcula el total y descuenta el stock.

        Todo ocurre en una sola transacción: si algo falla, no se guarda nada.
        """
        if data.client_id is not None and self.clients.get(data.client_id) is None:
            raise NotFoundError("Cliente no encontrado")
        quantities = self._group_quantities(data)
        products = self._validate_products(quantities)

        try:
            sale = Sale(client_id=data.client_id, user_id=user_id, date=datetime.now(), total=Decimal("0.00"))
            for product_id, quantity in quantities.items():
                product = products[product_id]
                sale.details.append(SaleDetail(
                    product_id=product_id, quantity=quantity, unit_price=product.price,
                    subtotal=calculate_subtotal(product.price, quantity),
                ))
            sale.total = calculate_total((p.price, quantities[pid]) for pid, p in products.items())
            self.sales.add(sale)
            for product_id, quantity in quantities.items():
                self.inventory.apply_movement(
                    products[product_id], -quantity, MOVEMENT_SALE,
                    reference=f"Venta #{sale.id}", user_id=user_id,
                )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return sale

    @staticmethod
    def _group_quantities(data: SaleCreate) -> dict[int, int]:
        """Si un producto se repite en la venta, se suman sus cantidades."""
        quantities: dict[int, int] = defaultdict(int)
        for item in data.items:
            quantities[item.product_id] += item.quantity
        return dict(quantities)

    def _validate_products(self, quantities: dict[int, int]) -> dict:
        products = {}
        for product_id, quantity in quantities.items():
            product = self.products.get(product_id)
            if product is None or not product.active:
                raise NotFoundError(f"Producto {product_id} no encontrado")
            if quantity > product.stock:
                raise InsufficientStockError(
                    f"Stock insuficiente de {product.name}: disponible {product.stock}, solicitado {quantity}"
                )
            products[product_id] = product
        return products
