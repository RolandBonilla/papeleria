# Pruebas

Se ejecutan con `python -m pytest` desde la raíz del proyecto. Cada prueba usa una base SQLite en memoria nueva con los datos iniciales, por lo que no dependen entre sí y nunca tocan `data/papeleria.db`.

## Casos de prueba principales

| ID | Tipo | Descripción | Resultado esperado | Archivo |
| --- | --- | --- | --- | --- |
| CP-01 | Unitaria | Calcular total: precio 2.50 x cantidad 3 | Total correcto: 7.50 | `tests/unit/test_sales.py` |
| CP-02 | Integración | Venta + inventario: stock inicial 10, venta de 3 | Stock actualizado: 7 | `tests/integration/test_sales_inventory.py` |
| CP-03 | Aceptación | Proceso completo de venta (seleccionar producto, cantidad, total, registrar, actualizar stock) | Venta completada | `tests/acceptance/test_sales_acceptance.py` |

## Otras pruebas

| Tipo | Qué comprueban | Archivo |
| --- | --- | --- |
| Unitaria | Cantidad cero, negativa y decimal; precio cero; múltiples productos; lista vacía; redondeo | `unit/test_sales.py` |
| Unitaria | Registro, código duplicado, validación de precio/stock, búsqueda por código/nombre/categoría, edición, baja lógica, símbolos `%` y `_` tratados como texto | `unit/test_products.py` |
| Unitaria | Ingreso de mercadería, estados de stock, alertas (RF-10), sin duplicados, alerta que se cierra, stock nunca negativo | `unit/test_inventory.py` |
| Unitaria | Singleton y Observer | `unit/test_patterns.py` |
| Unitaria | Hash de contraseñas, tokens (válido, manipulado, vencido), login | `unit/test_auth.py` |
| Unitaria | Clientes: registro, búsqueda, cédula duplicada/inválida, edición, símbolos `%` y `_` tratados como texto | `unit/test_clients.py` |
| Integración | Venta mayor al stock rechazada sin guardar nada; atomicidad con varios productos; líneas repetidas; alerta tras venta; cliente; errores 404; respuestas HTTP 409/422 | `integration/test_sales_inventory.py` |
| Aceptación | Alerta visible tras venta; RNF-02 (< 3 s); RNF-01 (401/403 por rol); ingreso de mercadería que resuelve la alerta; frontend servido | `acceptance/test_sales_acceptance.py` |

## Alcance y límites

- Total actual: 69 pruebas, todas con afirmaciones reales sobre la lógica (ninguna devuelve `True` fijo).
- Las pruebas de aceptación recorren la API tal como lo hace la interfaz web; **no hay pruebas automáticas del código JavaScript del navegador**. El frontend se verificó aparte (fuera del repositorio) ejecutando el JavaScript real de cada página con jsdom contra el servidor: inicio de sesión, resumen, productos, inventario, clientes, ventas, reportes y permisos por rol. Esa verificación no se ejecuta en GitHub Actions; conviene recorrer las pantallas en el navegador antes de tomar las capturas.
- No se mide cobertura de código.
