from src.ventas import calcular_total


def test_calcular_total_venta():
    # CP-01: verificar que el total de una venta sea correcto
    resultado = calcular_total(2.50, 3)

    assert resultado == 7.50