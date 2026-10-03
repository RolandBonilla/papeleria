# API REST

Base: `http://127.0.0.1:8000/api`. Documentación interactiva: `http://127.0.0.1:8000/docs`.

Todas las rutas, excepto el login, requieren la cabecera `Authorization: Bearer <token>`.

Errores: `401` sin sesión o token inválido, `403` rol sin permiso, `404` no existe, `409` duplicado o stock insuficiente, `422` datos inválidos. El cuerpo es `{"detail": "mensaje"}`.

## Autenticación

| Método | Ruta | Roles | Descripción |
| --- | --- | --- | --- |
| POST | `/auth/login` | público | Cuerpo: `{"username","password"}`. Devuelve `access_token`, `username`, `full_name`, `role`. |
| GET | `/auth/me` | todos | Usuario de la sesión. |

## Productos y categorías

| Método | Ruta | Roles | Descripción |
| --- | --- | --- | --- |
| GET | `/products` | todos | Filtros: `q` (código o nombre), `code`, `name`, `category_id`. |
| POST | `/products` | ADMINISTRADOR, INVENTARIO | `{"code","name","category_id","price","stock","min_stock"}` |
| GET | `/products/{id}` | todos | Un producto. |
| PUT | `/products/{id}` | ADMINISTRADOR, INVENTARIO | Edita código, nombre, categoría, precio y stock mínimo. |
| DELETE | `/products/{id}` | ADMINISTRADOR, INVENTARIO | Baja lógica (204). |
| GET | `/categories` | todos | Lista de categorías. |
| POST | `/categories` | ADMINISTRADOR, INVENTARIO | `{"name"}` |

## Clientes

| Método | Ruta | Roles | Descripción |
| --- | --- | --- | --- |
| GET | `/clients` | todos | Filtro `q` (cédula o nombre). |
| POST | `/clients` | ADMINISTRADOR, VENDEDOR | `{"cedula","name","phone","email"}` (cédula: 10 dígitos). |
| GET | `/clients/{id}` | todos | Un cliente. |
| PUT | `/clients/{id}` | ADMINISTRADOR, VENDEDOR | Edita un cliente. |

## Ventas

| Método | Ruta | Roles | Descripción |
| --- | --- | --- | --- |
| GET | `/sales` | ADMINISTRADOR, VENDEDOR | Lista de ventas. Filtros: `date_from`, `date_to` (AAAA-MM-DD). |
| POST | `/sales` | ADMINISTRADOR, VENDEDOR | Registra una venta. |
| GET | `/sales/{id}` | ADMINISTRADOR, VENDEDOR | Una venta. |

Ejemplo de `POST /sales`:

```json
{ "client_id": 1, "items": [ { "product_id": 1, "quantity": 3 } ] }
```

Respuesta `201`:

```json
{
  "id": 1, "date": "2026-10-03T10:15:00", "client_id": 1, "client_name": "María Pérez",
  "total": "7.50",
  "details": [ { "product_id": 1, "product_name": "Cuaderno universitario",
                 "quantity": 3, "unit_price": "2.50", "subtotal": "7.50" } ]
}
```

`client_id` es opcional. Si se pide más cantidad que el stock, responde `409` y no se guarda nada.

## Inventario

| Método | Ruta | Roles | Descripción |
| --- | --- | --- | --- |
| GET | `/inventory` | todos | Producto, stock, mínimo y estado (`Disponible`, `Stock bajo`, `Sin stock`). Filtro `status`. |
| GET | `/inventory/low-stock` | todos | Productos con stock <= mínimo. |
| GET | `/inventory/alerts` | todos | Alertas de stock abiertas. |
| POST | `/inventory/entries` | ADMINISTRADOR, INVENTARIO | Ingreso de mercadería: `{"product_id","quantity","note"}`. |

## Reportes

| Método | Ruta | Roles | Descripción |
| --- | --- | --- | --- |
| GET | `/reports/sales` | ADMINISTRADOR, VENDEDOR | `{"sales":[...],"count","total"}`. Filtros `date_from`, `date_to`. |
| GET | `/reports/low-stock` | todos | Productos con stock bajo. |
| GET | `/reports/dashboard` | todos | Total de productos, productos con stock bajo, ventas de hoy y total vendido hoy. |
