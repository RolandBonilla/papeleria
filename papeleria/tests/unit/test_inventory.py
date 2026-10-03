import pytest
from sqlalchemy import select

from app.exceptions import InsufficientStockError, InvalidDataError, NotFoundError
from app.models.stock_movement import MOVEMENT_ENTRY, MOVEMENT_SALE, StockMovement
from app.repositories.product_repository import ProductRepository
from app.services.inventory_service import InventoryService


def test_ingreso_de_mercaderia_aumenta_el_stock_y_queda_registrado(db, make_product):
    product = make_product(stock=5)
    InventoryService(db).register_entry(product.id, 7, note="Pedido proveedor")
    assert ProductRepository(db).get(product.id).stock == 12
    movement = db.scalars(select(StockMovement).where(
        StockMovement.product_id == product.id, StockMovement.type == MOVEMENT_ENTRY)).one()
    assert movement.quantity == 7


@pytest.mark.parametrize("quantity", [0, -3])
def test_ingreso_con_cantidad_invalida_es_rechazado(db, make_product, quantity):
    product = make_product(stock=5)
    with pytest.raises(InvalidDataError):
        InventoryService(db).register_entry(product.id, quantity)
    assert ProductRepository(db).get(product.id).stock == 5


def test_ingreso_a_producto_inexistente_es_rechazado(db):
    with pytest.raises(NotFoundError):
        InventoryService(db).register_entry(9999, 1)


def test_estados_de_stock(make_product):
    assert make_product(code="E1", stock=10, min_stock=5).stock_status == "Disponible"
    assert make_product(code="E2", stock=5, min_stock=5).stock_status == "Stock bajo"
    assert make_product(code="E3", stock=0, min_stock=5).stock_status == "Sin stock"


def test_lista_de_inventario_se_filtra_por_estado(db):
    service = InventoryService(db)
    assert [p.code for p in service.list_inventory("Stock bajo")] == ["PAP004"]
    assert len(service.list_inventory()) == 4


def test_rf10_producto_inicial_con_stock_bajo_genera_alerta(db):
    alerts = InventoryService(db).open_alerts()
    assert [a.product_name for a in alerts] == ["Resma de papel A4"]
    assert "Stock bajo" in alerts[0].message


def test_stock_igual_al_minimo_genera_alerta(db, make_product):
    producto = make_product(code="LIM1", stock=5, min_stock=5)
    assert producto.id in [a.product_id for a in InventoryService(db).open_alerts()]


def test_no_se_duplican_alertas_para_el_mismo_producto(db):
    service = InventoryService(db)
    producto = ProductRepository(db).get_by_code("PAP004")
    service.notify_stock_changed(producto)
    service.notify_stock_changed(producto)
    assert len([a for a in service.open_alerts() if a.product_id == producto.id]) == 1


def test_alerta_se_cierra_cuando_el_stock_se_recupera(db):
    service = InventoryService(db)
    producto = ProductRepository(db).get_by_code("PAP004")
    service.register_entry(producto.id, 10)
    assert producto.id not in [a.product_id for a in service.open_alerts()]


def test_el_stock_no_puede_quedar_negativo(db, make_product):
    producto = make_product(stock=2)
    with pytest.raises(InsufficientStockError):
        InventoryService(db).apply_movement(producto, -3, MOVEMENT_SALE)
    assert producto.stock == 2


def test_productos_con_stock_bajo(db, make_product):
    make_product(code="LOW1", stock=1, min_stock=3)
    codigos = [p.code for p in InventoryService(db).low_stock_products()]
    assert "LOW1" in codigos and "PAP004" in codigos and "PAP001" not in codigos
