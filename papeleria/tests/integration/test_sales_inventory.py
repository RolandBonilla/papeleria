"""Integración: ventas + inventario + alertas trabajando juntos sobre la base de datos."""
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.exceptions import InsufficientStockError, NotFoundError
from app.models.stock_movement import MOVEMENT_SALE, StockMovement
from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository
from app.schemas.client import ClientCreate
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.client_service import ClientService
from app.services.inventory_service import InventoryService
from app.services.sale_service import SaleService


def venta(*items, client_id=None):
    return SaleCreate(client_id=client_id, items=[SaleItemCreate(product_id=p, quantity=q) for p, q in items])


def stock_de(db, product_id):
    return ProductRepository(db).get(product_id).stock


def test_cp02_venta_disminuye_el_inventario(db, make_product):
    producto = make_product(code="CP02", price="2.50", stock=10)
    sale = SaleService(db).create_sale(venta((producto.id, 3)))
    assert stock_de(db, producto.id) == 7
    assert sale.total == Decimal("7.50")
    movimiento = db.scalars(select(StockMovement).where(
        StockMovement.product_id == producto.id, StockMovement.type == MOVEMENT_SALE)).one()
    assert movimiento.quantity == -3


def test_venta_mayor_al_stock_es_rechazada_sin_guardar_nada(db, make_product):
    producto = make_product(stock=2)
    with pytest.raises(InsufficientStockError):
        SaleService(db).create_sale(venta((producto.id, 3)))
    assert stock_de(db, producto.id) == 2
    assert SaleRepository(db).list() == []


def test_venta_con_varios_productos_es_atomica(db, make_product):
    a = make_product(code="A1", stock=10)
    b = make_product(code="B1", stock=1)
    with pytest.raises(InsufficientStockError):
        SaleService(db).create_sale(venta((a.id, 2), (b.id, 5)))
    assert stock_de(db, a.id) == 10
    assert stock_de(db, b.id) == 1


def test_lineas_repetidas_del_mismo_producto_se_suman(db, make_product):
    producto = make_product(stock=3)
    with pytest.raises(InsufficientStockError):
        SaleService(db).create_sale(venta((producto.id, 2), (producto.id, 2)))
    sale = SaleService(db).create_sale(venta((producto.id, 1), (producto.id, 2)))
    assert [d.quantity for d in sale.details] == [3]
    assert stock_de(db, producto.id) == 0


def test_venta_multiple_calcula_subtotales_y_total(db, make_product):
    a = make_product(code="M1", price="2.50", stock=10)
    b = make_product(code="M2", price="0.50", stock=50)
    sale = SaleService(db).create_sale(venta((a.id, 3), (b.id, 10)))
    assert [d.subtotal for d in sale.details] == [Decimal("7.50"), Decimal("5.00")]
    assert sale.total == Decimal("12.50")


def test_venta_que_deja_stock_bajo_genera_alerta(db, make_product):
    producto = make_product(code="AL1", stock=6, min_stock=5)
    assert producto.id not in [a.product_id for a in InventoryService(db).open_alerts()]
    SaleService(db).create_sale(venta((producto.id, 2)))
    assert producto.id in [a.product_id for a in InventoryService(db).open_alerts()]


def test_venta_con_cliente_registrado(db, make_product):
    producto = make_product()
    cliente = ClientService(db).create(ClientCreate(cedula="1799999999", name="Laura Vega"))
    sale = SaleService(db).create_sale(venta((producto.id, 1), client_id=cliente.id))
    assert sale.client_name == "Laura Vega"


def test_venta_con_producto_o_cliente_inexistente(db, make_product):
    producto = make_product()
    with pytest.raises(NotFoundError):
        SaleService(db).create_sale(venta((9999, 1)))
    with pytest.raises(NotFoundError):
        SaleService(db).create_sale(venta((producto.id, 1), client_id=9999))


def test_api_venta_superior_al_stock_responde_409_y_no_cambia_el_stock(client, vendedor_headers):
    producto = client.get("/api/products?code=PAP004", headers=vendedor_headers).json()[0]
    respuesta = client.post("/api/sales", headers=vendedor_headers,
                            json={"items": [{"product_id": producto["id"], "quantity": 4}]})
    assert respuesta.status_code == 409
    assert "Stock insuficiente" in respuesta.json()["detail"]
    assert client.get(f"/api/products/{producto['id']}", headers=vendedor_headers).json()["stock"] == 3


def test_api_registro_de_producto_y_validaciones(client, admin_headers):
    categoria = client.get("/api/categories", headers=admin_headers).json()[0]
    cuerpo = {"code": "api1", "name": "Marcador", "category_id": categoria["id"],
              "price": "1.25", "stock": 10, "min_stock": 2}
    creado = client.post("/api/products", headers=admin_headers, json=cuerpo)
    assert creado.status_code == 201
    assert creado.json()["code"] == "API1"
    assert client.post("/api/products", headers=admin_headers, json=cuerpo).status_code == 409
    assert client.post("/api/products", headers=admin_headers, json={**cuerpo, "code": "API2", "price": "0"}).status_code == 422
