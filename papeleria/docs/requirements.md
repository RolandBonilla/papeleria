# Especificación de requerimientos

## Contexto

Una papelería pequeña vende útiles escolares y de oficina. Hoy registra productos, inventario, ventas y clientes de forma manual (cuadernos y hojas sueltas).

## Problema

- Los totales de las ventas se calculan a mano y pueden tener errores.
- No hay forma rápida de saber cuánto stock queda de cada producto.
- Se detecta tarde que un producto se está acabando.
- No existe un historial consultable de ventas ni de clientes.

## Actores

| Actor | Rol en el sistema | Qué hace |
| --- | --- | --- |
| Administrador | `ADMINISTRADOR` | Acceso completo: productos, inventario, ventas, clientes y reportes. |
| Vendedor | `VENDEDOR` | Registra ventas y clientes; consulta productos, stock y reporte de ventas. |
| Encargado de inventario | `INVENTARIO` | Registra productos y el ingreso de mercadería; consulta stock y alertas. |

## Requerimientos funcionales

| ID | Requerimiento | Dónde se implementa | Estado |
| --- | --- | --- | --- |
| RF-01 | Registrar productos (código, nombre, categoría, precio, stock actual, stock mínimo) | `POST /api/products`, `ProductService.create` | Implementado |
| RF-02 | Consultar productos por código, nombre o categoría | `GET /api/products` (`code`, `name`, `category_id`, `q`) | Implementado |
| RF-03 | Actualizar datos de un producto | `PUT /api/products/{id}` | Implementado (ver nota) |
| RF-04 | Registrar ingreso de mercadería | `POST /api/inventory/entries` | Implementado |
| RF-05 | Registrar venta con uno o varios productos (fecha, cliente opcional, cantidades, precio unitario, subtotal, total) | `POST /api/sales`, `SaleService.create_sale` | Implementado |
| RF-06 | Calcular automáticamente el total | `calculate_subtotal` y `calculate_total` en `sale_service.py` | Implementado |
| RF-07 | Actualizar el inventario tras una venta y no vender más que el stock | `SaleService` + `InventoryService.apply_movement` | Implementado |
| RF-08 | Registrar clientes (cédula, nombre, teléfono, correo) | `POST /api/clients` | Implementado |
| RF-09 | Consultar clientes | `GET /api/clients?q=` | Implementado |
| RF-10 | Generar alerta cuando `stock_actual <= stock_minimo` | `LowStockAlertObserver` (patrón Observer) | Implementado |
| RF-11 | Reporte de ventas realizadas | `GET /api/reports/sales` | Implementado |
| RF-12 | Reporte de productos con stock bajo | `GET /api/reports/low-stock` | Implementado |

Decisiones y notas de diseño:

- **RF-03:** el stock no se modifica con la edición del producto. Solo cambia por ingresos y ventas, para que cada cambio quede registrado en `stock_movements`.
- **Eliminar producto:** es una baja lógica (`active = false`). Así no se pierde el historial de ventas.
- **Precio cero:** un producto no puede tener precio 0 y una línea de venta con precio 0 se rechaza.
- **Cédula:** se valida solo el formato (10 dígitos); no se comprueba el dígito verificador.
- **Productos repetidos en una venta:** sus cantidades se suman antes de validar el stock.

## Requerimientos no funcionales

| ID | Requerimiento | Cómo se cubre | Evidencia |
| --- | --- | --- | --- |
| RNF-01 | Autenticación con usuario/contraseña y roles | Login con contraseñas PBKDF2, token firmado y control de roles en cada ruta | `tests/unit/test_auth.py`, `test_rnf01_...` |
| RNF-02 | Registrar una venta en menos de 3 s en entorno local | Una sola transacción SQLite local | `test_rnf02_...` |
| RNF-03 | Interfaz sencilla | Páginas simples con formularios y tablas, mensajes claros | Revisión manual (sin pruebas con usuarios) |
| RNF-04 | Disponibilidad en el horario de atención | La aplicación corre localmente sin servicios externos; el sistema no incluye mecanismos de alta disponibilidad: depende de dejar el servidor encendido | Documentado, no automatizado |
| RNF-05 | Confiabilidad de la información | Validación con Pydantic y reglas de negocio; ventas en una transacción (todo o nada); claves foráneas activas | Pruebas de integración de atomicidad |
