"""Pruebas unitarias del cálculo de totales (RF-06). No usan base de datos."""
from decimal import Decimal

import pytest

from app.services.sale_service import calculate_subtotal, calculate_total


def test_cp01_calcula_total_precio_2_50_por_3():
    resultado = calculate_subtotal(Decimal("2.50"), 3)
    assert resultado == Decimal("7.50")
    assert str(resultado) == "7.50"


def test_cantidad_cero_es_rechazada():
    with pytest.raises(ValueError):
        calculate_subtotal(Decimal("2.50"), 0)


def test_cantidad_negativa_es_rechazada():
    with pytest.raises(ValueError):
        calculate_subtotal(Decimal("2.50"), -2)


def test_precio_cero_es_rechazado():
    with pytest.raises(ValueError):
        calculate_subtotal(Decimal("0"), 3)


def test_cantidad_decimal_es_rechazada():
    with pytest.raises(ValueError):
        calculate_subtotal(Decimal("2.50"), 1.5)


def test_total_de_multiples_productos():
    items = [(Decimal("2.50"), 3), (Decimal("0.50"), 10), (Decimal("5.50"), 1)]
    assert calculate_total(items) == Decimal("18.00")


def test_total_sin_productos_es_rechazado():
    with pytest.raises(ValueError):
        calculate_total([])


def test_acepta_precio_como_texto_o_float_sin_errores_de_redondeo():
    assert calculate_subtotal("0.10", 3) == Decimal("0.30")
    assert calculate_subtotal(2.5, 3) == Decimal("7.50")
