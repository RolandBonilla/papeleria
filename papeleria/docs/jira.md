# Historias de usuario para Jira

Proyecto individual. Responsable de todas las historias: **Desarrollador**.

## HU-01 – Registrar productos

**Como** encargado de inventario, **quiero** registrar productos **para** mantener actualizado el inventario.

**Descripción:** el encargado ingresa código, nombre, categoría, precio, stock inicial y stock mínimo de un producto nuevo, y puede editarlo o buscarlo después.

**Criterios de aceptación:**

- Se puede guardar un producto con código, nombre, categoría, precio, stock actual y stock mínimo.
- No se permite repetir el código de un producto.
- No se permite precio igual o menor que cero, ni stock negativo.
- El producto registrado aparece en la lista y se puede buscar por código, nombre o categoría.
- Un producto con stock menor o igual al mínimo genera una alerta.

**Tareas:**

- Crear modelos `Product` y `Category`.
- Crear `ProductRepository` y `ProductService`.
- Crear endpoints `POST/GET/PUT/DELETE /api/products` y `/api/categories`.
- Crear la pantalla `products.html` con formulario, búsqueda y tabla.
- Escribir pruebas unitarias de productos.

**Prioridad:** Alta
**Responsable sugerido:** Desarrollador

## HU-02 – Registrar una venta

**Como** vendedor, **quiero** registrar una venta **para** calcular automáticamente el total y controlar la salida de productos.

**Descripción:** el vendedor elige un cliente (opcional), agrega productos con su cantidad, ve subtotales y total, y registra la venta. El sistema descuenta el stock.

**Criterios de aceptación:**

- El subtotal de cada producto es precio por cantidad (2.50 x 3 = 7.50) y el total es la suma de subtotales.
- Al registrar la venta, el stock de cada producto disminuye en la cantidad vendida.
- No se permite vender más unidades que el stock disponible; en ese caso no se guarda nada.
- No se aceptan cantidades cero o negativas.
- La venta guarda fecha, cliente opcional, productos, cantidades, precios unitarios, subtotales y total.
- Si el stock queda menor o igual al mínimo, se genera una alerta.

**Tareas:**

- Crear modelos `Sale` y `SaleDetail`.
- Implementar `calculate_subtotal` y `calculate_total`.
- Implementar `SaleService.create_sale` en una sola transacción.
- Implementar el patrón Observer para las alertas.
- Crear `POST /api/sales` y la pantalla `sales.html`.
- Escribir pruebas CP-01, CP-02 y CP-03.

**Prioridad:** Alta
**Responsable sugerido:** Desarrollador

## HU-03 – Consultar disponibilidad de productos

**Como** vendedor, **quiero** consultar la disponibilidad de productos **para** conocer el stock antes de realizar una venta.

**Descripción:** el vendedor revisa el stock actual y el estado de cada producto (Disponible, Stock bajo, Sin stock).

**Criterios de aceptación:**

- La pantalla de inventario muestra producto, stock actual, stock mínimo y estado.
- El estado es "Sin stock" si el stock es 0, "Stock bajo" si es menor o igual al mínimo, y "Disponible" en los demás casos.
- Se puede filtrar por estado.
- En la pantalla de ventas, cada producto muestra su stock y no se pueden elegir los que no tienen.

**Tareas:**

- Crear `GET /api/inventory` y `GET /api/inventory/low-stock`.
- Crear la pantalla `inventory.html`.
- Mostrar el stock en la lista de productos de `sales.html`.
- Escribir pruebas de estados de stock.

**Prioridad:** Media
**Responsable sugerido:** Desarrollador

## HU-04 – Registrar ingreso de mercadería

**Como** encargado de inventario, **quiero** registrar el ingreso de mercadería **para** aumentar el stock cuando llega un pedido.

**Descripción:** el encargado elige un producto e indica cuántas unidades llegaron.

**Criterios de aceptación:**

- Se puede indicar producto y cantidad mayor que cero.
- El stock aumenta y queda un movimiento registrado.
- Si el stock supera el mínimo, la alerta de ese producto se cierra.

**Tareas:**

- Crear `POST /api/inventory/entries`.
- Crear el formulario de ingreso en `inventory.html`.
- Escribir pruebas de ingreso de mercadería.

**Prioridad:** Alta
**Responsable sugerido:** Desarrollador

## HU-05 – Registrar y consultar clientes

**Como** vendedor, **quiero** registrar y consultar clientes **para** asociarlos a las ventas.

**Descripción:** el vendedor guarda los datos de un cliente, lo busca y corrige su información.

**Criterios de aceptación:**

- Se registran cédula (10 dígitos), nombre, teléfono y correo.
- No se permite repetir la cédula.
- Se puede buscar por cédula o nombre y editar un cliente.

**Tareas:**

- Crear el modelo `Client` y `ClientService`.
- Crear endpoints `/api/clients`.
- Crear la pantalla `clients.html`.
- Escribir pruebas de clientes.

**Prioridad:** Media
**Responsable sugerido:** Desarrollador

## HU-06 – Consultar reportes

**Como** administrador, **quiero** consultar las ventas realizadas y los productos con stock bajo **para** tomar decisiones de compra.

**Descripción:** el administrador revisa el historial de ventas y la lista de productos que debe reponer.

**Criterios de aceptación:**

- El reporte de ventas lista fecha, cliente, productos y total, con filtro por fechas y suma total.
- El reporte de stock bajo lista los productos con stock menor o igual al mínimo.

**Tareas:**

- Crear `ReportService`.
- Crear endpoints `/api/reports/*`.
- Crear la pantalla `reports.html`.
- Escribir pruebas de reportes.

**Prioridad:** Media
**Responsable sugerido:** Desarrollador

## HU-07 – Iniciar sesión con roles

**Como** administrador, **quiero** que cada usuario inicie sesión y tenga permisos según su rol **para** proteger la información.

**Descripción:** cada persona entra con usuario y contraseña y solo puede hacer lo que su rol permite.

**Criterios de aceptación:**

- Se accede con usuario y contraseña; las contraseñas se guardan con hash.
- Sin sesión, la API responde 401; con un rol sin permiso, responde 403.
- Existen los roles ADMINISTRADOR, VENDEDOR e INVENTARIO.

**Tareas:**

- Crear `AuthService` y la dependencia `require_roles`.
- Crear la pantalla `login.html`.
- Escribir pruebas de autenticación y permisos.

**Prioridad:** Alta
**Responsable sugerido:** Desarrollador
