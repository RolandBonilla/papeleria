"""Aceptación: recorre el proceso completo de venta como lo haría el vendedor desde la interfaz."""
import time
from decimal import Decimal


def test_cp03_proceso_completo_de_venta(client, vendedor_headers):
    # 1. Seleccionar producto
    producto = client.get("/api/products?code=PAP001", headers=vendedor_headers).json()[0]
    assert producto["stock"] == 20

    # 2. Indicar cantidad y 3. Calcular total
    cantidad = 3
    total_esperado = Decimal(producto["price"]) * cantidad
    assert total_esperado == Decimal("7.50")

    # 4. Registrar venta
    respuesta = client.post("/api/sales", headers=vendedor_headers,
                            json={"items": [{"product_id": producto["id"], "quantity": cantidad}]})
    assert respuesta.status_code == 201
    venta = respuesta.json()
    assert Decimal(venta["total"]) == total_esperado
    assert venta["details"][0]["subtotal"] == "7.50"

    # 5. Actualizar stock
    inventario = {i["code"]: i for i in client.get("/api/inventory", headers=vendedor_headers).json()}
    assert inventario["PAP001"]["stock"] == 17

    # La venta aparece en los reportes y en el resumen del día
    reporte = client.get("/api/reports/sales", headers=vendedor_headers).json()
    assert reporte["count"] == 1 and Decimal(reporte["total"]) == Decimal("7.50")
    resumen = client.get("/api/reports/dashboard", headers=vendedor_headers).json()
    assert resumen["sales_today"] == 1 and Decimal(resumen["total_sold_today"]) == Decimal("7.50")


def test_venta_que_deja_el_stock_en_el_minimo_muestra_alerta(client, vendedor_headers):
    producto = client.get("/api/products?code=PAP003", headers=vendedor_headers).json()[0]
    client.post("/api/sales", headers=vendedor_headers,
                json={"items": [{"product_id": producto["id"], "quantity": 3}]})
    alertas = client.get("/api/inventory/alerts", headers=vendedor_headers).json()
    nombres = [a["product_name"] for a in alertas]
    assert "Carpeta manila" in nombres and "Resma de papel A4" in nombres


def test_rnf02_registrar_una_venta_tarda_menos_de_3_segundos(client, vendedor_headers):
    producto = client.get("/api/products?code=PAP002", headers=vendedor_headers).json()[0]
    inicio = time.perf_counter()
    respuesta = client.post("/api/sales", headers=vendedor_headers,
                            json={"items": [{"product_id": producto["id"], "quantity": 2}]})
    assert respuesta.status_code == 201
    assert time.perf_counter() - inicio < 3


def test_rnf01_acceso_sin_sesion_y_por_rol(client, inventario_headers):
    assert client.get("/api/products").status_code == 401
    assert client.get("/api/products", headers={"Authorization": "Bearer falso"}).status_code == 401
    producto = client.get("/api/products?code=PAP001", headers=inventario_headers).json()[0]
    venta = {"items": [{"product_id": producto["id"], "quantity": 1}]}
    assert client.post("/api/sales", headers=inventario_headers, json=venta).status_code == 403


def test_login_incorrecto_responde_401(client):
    respuesta = client.post("/api/auth/login", json={"username": "admin", "password": "mala"})
    assert respuesta.status_code == 401


def test_ingreso_de_mercaderia_por_api_resuelve_la_alerta(client, inventario_headers):
    producto = client.get("/api/products?code=PAP004", headers=inventario_headers).json()[0]
    respuesta = client.post("/api/inventory/entries", headers=inventario_headers,
                            json={"product_id": producto["id"], "quantity": 10})
    assert respuesta.status_code == 201
    assert respuesta.json()["stock"] == 13
    assert respuesta.json()["stock_status"] == "Disponible"
    assert client.get("/api/reports/low-stock", headers=inventario_headers).json() == []


def test_vendedor_no_puede_registrar_ingresos(client, vendedor_headers):
    respuesta = client.post("/api/inventory/entries", headers=vendedor_headers,
                            json={"product_id": 1, "quantity": 5})
    assert respuesta.status_code == 403


def test_frontend_es_servido_por_fastapi(client):
    assert "Iniciar sesión" in client.get("/login.html").text
    assert client.get("/").status_code == 200
