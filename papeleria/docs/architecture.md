# Arquitectura

## Arquitectura en capas (tres niveles)

```text
Navegador (frontend/*.html, js/*.js)
        │  HTTP + JSON
        ▼
┌───────────────────────────────┐
│ 1. PRESENTACIÓN               │  app/api/*  (rutas, roles, respuestas HTTP)
│    Rutas FastAPI + Pydantic   │  app/schemas/*  (validación de entrada/salida)
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 2. LÓGICA DE NEGOCIO          │  app/services/*
│    Reglas del sistema         │  (totales, stock, alertas, autenticación)
└───────────────┬───────────────┘
                ▼
┌───────────────────────────────┐
│ 3. ACCESO A DATOS             │  app/repositories/*  (consultas)
│    Repositorios + modelos     │  app/models/*  (tablas)
└───────────────┬───────────────┘  app/database/*  (conexión, creación de BD)
                ▼
             SQLite (data/papeleria.db)
```

Reglas de separación:

- Las rutas no contienen reglas de negocio: reciben datos, llaman a un servicio y devuelven el resultado.
- Los servicios no conocen HTTP: lanzan errores de negocio (`app/exceptions.py`) y `app/main.py` los convierte en códigos HTTP.
- Solo los repositorios construyen consultas a la base de datos.
- Las funciones de cálculo (`calculate_subtotal`, `calculate_total`) no usan base de datos, por eso se prueban de forma unitaria.

## Patrón Singleton

**Problema:** si cada parte del sistema creara su propia conexión, habría varios motores de base de datos y configuraciones distintas.

**Solución:** `SingletonMeta` (`app/patterns/singleton.py`) es una metaclase que guarda la única instancia de cada clase. `DatabaseManager` (`app/database/connection.py`) la usa:

```python
class DatabaseManager(metaclass=SingletonMeta):
    ...

DatabaseManager() is DatabaseManager()   # True
```

La primera llamada crea el motor y la fábrica de sesiones; las siguientes devuelven el mismo objeto. Un candado (`threading.Lock`) evita que dos hilos creen dos instancias. Prueba: `test_database_manager_siempre_devuelve_la_misma_instancia`.

## Patrón Observer

**Problema:** al cambiar el stock, el sistema debe reaccionar (crear alertas) sin que el código de ventas conozca los detalles de las alertas.

**Solución:** `Subject` y `Observer` (`app/patterns/observer.py`).

- Evento: `StockChangedEvent` (producto + sesión de base de datos).
- Subject: `stock_subject`, que notifica cuando cambia el stock (venta, ingreso, producto nuevo, cambio del mínimo o baja del producto).
- Observer: `LowStockAlertObserver` (`app/services/inventory_service.py`):
  - si `stock <= stock_minimo`: crea una alerta (o actualiza el mensaje de la abierta, sin duplicar);
  - si el stock se recuperó: marca la alerta como resuelta.

Se pueden agregar más observadores (por ejemplo, enviar un correo) sin modificar el código de ventas.

## Flujo de una venta

```text
POST /api/sales  (rol VENDEDOR o ADMINISTRADOR)
   │  routes_sales.create_sale: valida el cuerpo con Pydantic (cantidad > 0, al menos un producto)
   ▼
SaleService.create_sale
   1. Verifica que el cliente (si se indicó) exista
   2. Suma cantidades repetidas del mismo producto
   3. Verifica que cada producto exista y que cantidad <= stock  → si no, 409 y no se guarda nada
   4. Calcula subtotales y total (calculate_subtotal / calculate_total)
   5. Guarda la venta y sus detalles
   6. Para cada producto: InventoryService.apply_movement
         stock nuevo = stock anterior - cantidad vendida
         registra el movimiento en stock_movements
         stock_subject.notify(...)  ──►  LowStockAlertObserver
                                              └─ si stock <= mínimo: crea la alerta
   7. commit (todo o nada; ante cualquier error se hace rollback)
   ▼
201 + venta con detalles y total
```

## Modelo de datos

`users`, `categories`, `products`, `clients`, `sales`, `sale_details`, `stock_movements`, `alerts`.

Los precios se guardan como enteros en centavos (tipo `Money` en `app/database/types.py`) y se devuelven como `Decimal`, para evitar errores de redondeo con decimales binarios.
