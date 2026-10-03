from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.exceptions import DuplicateError, NotFoundError
from app.repositories.product_repository import CategoryRepository
from app.schemas.product import CategoryCreate, ProductCreate, ProductUpdate
from app.services.product_service import ProductService


def test_registrar_producto_guarda_los_datos(db, make_product):
    product = make_product(code=" abc1 ", name="Lápiz HB", price="0.35", stock=12, min_stock=4)
    assert product.id is not None
    assert (product.code, product.name) == ("ABC1", "Lápiz HB")
    assert product.price == Decimal("0.35")
    assert (product.stock, product.min_stock) == (12, 4)


def test_codigo_duplicado_es_rechazado(make_product):
    make_product(code="DUP1")
    with pytest.raises(DuplicateError):
        make_product(code="dup1")


def test_esquema_rechaza_precio_cero_y_stock_negativo():
    base = {"code": "X1", "name": "X", "category_id": 1, "min_stock": 0}
    with pytest.raises(ValidationError):
        ProductCreate(**base, price=Decimal("0"))
    with pytest.raises(ValidationError):
        ProductCreate(**base, price=Decimal("1.00"), stock=-1)
    with pytest.raises(ValidationError):
        ProductCreate(**base, price=Decimal("1.005"))


def test_categoria_inexistente_es_rechazada(db):
    with pytest.raises(NotFoundError):
        ProductService(db).create(ProductCreate(
            code="Z1", name="Z", category_id=9999, price=Decimal("1"), min_stock=0))


def test_buscar_por_codigo_nombre_y_categoria(db):
    service = ProductService(db)
    assert [p.code for p in service.search(code="PAP001")] == ["PAP001"]
    assert [p.code for p in service.search(name="esfero")] == ["PAP002"]
    escritura = CategoryRepository(db).get_by_name("Escritura")
    assert [p.code for p in service.search(category_id=escritura.id)] == ["PAP002"]
    assert service.search(q="no-existe") == []


def test_actualizar_producto_cambia_datos_pero_no_el_stock(db):
    service = ProductService(db)
    original = service.search(code="PAP001")[0]
    category_id = original.category_id
    updated = service.update(original.id, ProductUpdate(
        code="PAP001", name="Cuaderno 100 hojas", category_id=category_id,
        price=Decimal("3.00"), min_stock=8))
    assert updated.name == "Cuaderno 100 hojas"
    assert updated.price == Decimal("3.00")
    assert updated.stock == 20


def test_actualizar_con_codigo_de_otro_producto_es_rechazado(db):
    service = ProductService(db)
    producto = service.search(code="PAP001")[0]
    with pytest.raises(DuplicateError):
        service.update(producto.id, ProductUpdate(
            code="PAP002", name=producto.name, category_id=producto.category_id,
            price=producto.price, min_stock=producto.min_stock))


def test_eliminar_producto_lo_oculta_de_las_consultas(db):
    service = ProductService(db)
    producto = service.search(code="PAP003")[0]
    service.delete(producto.id)
    assert service.search(code="PAP003") == []
    with pytest.raises(NotFoundError):
        service.get(producto.id)


def test_categoria_duplicada_es_rechazada(db):
    with pytest.raises(DuplicateError):
        ProductService(db).create_category(CategoryCreate(name="cuadernos"))


def test_categoria_con_simbolos_comodin_no_choca_con_otra_existente(db):
    service = ProductService(db)
    assert service.create_category(CategoryCreate(name="Papel%")).name == "Papel%"
    assert service.create_category(CategoryCreate(name="Pape_")).name == "Pape_"


def test_busqueda_trata_porcentaje_y_guion_bajo_como_texto(db):
    service = ProductService(db)
    assert service.search(q="%") == []
    assert service.search(name="_") == []
