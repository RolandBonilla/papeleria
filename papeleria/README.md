# Sistema de Control de Inventario y Ventas para una Papelería

## Descripción

Una papelería pequeña lleva hoy sus productos, inventario, ventas y clientes en registros manuales. Eso provoca errores en los totales, stock desactualizado y ventas de productos que ya no hay.

Este proyecto es un sistema web sencillo que reemplaza esos registros: permite administrar productos, registrar ingresos de mercadería y ventas (con cálculo automático del total y descuento del stock), gestionar clientes y consultar reportes. Cuando un producto llega al stock mínimo, el sistema genera una alerta.

Es un trabajo práctico-experimental individual de la materia Ingeniería de Software.

## Objetivos

**General:** desarrollar un sistema que permita administrar de forma organizada los procesos principales de una papelería, aplicando buenas prácticas de Ingeniería de Software.

**Específicos:**

- Registrar y consultar productos, categorías, clientes y usuarios.
- Controlar el inventario: ingresos, salidas por venta y alertas de stock bajo.
- Registrar ventas con cálculo automático del total y validación de stock.
- Generar reportes de ventas y de productos con stock bajo.
- Aplicar arquitectura en capas y los patrones Singleton y Observer.
- Verificar el sistema con pruebas unitarias, de integración y de aceptación, ejecutadas automáticamente con GitHub Actions.

## Tecnologías

- Python 3.14 (probado con 3.14.4)
- FastAPI (API REST) y Uvicorn
- SQLAlchemy 2 y SQLite
- Pydantic (validación)
- HTML, CSS y JavaScript sin frameworks (servidos por FastAPI)
- pytest y httpx2 (pruebas; es el cliente HTTP que usa el `TestClient` de FastAPI/Starlette)
- Git, GitHub y GitHub Actions

## Arquitectura

Tres capas, cada una solo conoce a la capa inferior:

1. **Presentación:** `frontend/` (páginas HTML) y `app/api/` (rutas REST y esquemas Pydantic de entrada/salida).
2. **Lógica de negocio:** `app/services/` (reglas: cálculo de totales, validación de stock, alertas, autenticación).
3. **Acceso a datos:** `app/repositories/` (consultas), `app/models/` (tablas) y `app/database/` (conexión y creación de la base).

Más detalle en [docs/architecture.md](docs/architecture.md).

## Patrones

- **Singleton** (`app/patterns/singleton.py`, usado en `app/database/connection.py`): `DatabaseManager` tiene una única instancia que crea el motor de base de datos y las sesiones. Cualquier parte del sistema que lo pida recibe el mismo objeto.
- **Observer** (`app/patterns/observer.py`, usado en `app/services/inventory_service.py`): cada vez que cambia el stock de un producto, el `Subject` avisa a sus observadores. `LowStockAlertObserver` crea una alerta si `stock <= stock mínimo` y la cierra cuando el stock se recupera.

## Estructura

```text
papeleria/
├── app/
│   ├── main.py                  # Arranque de FastAPI + frontend
│   ├── config.py                # Configuración (variables de entorno)
│   ├── exceptions.py            # Errores de negocio
│   ├── api/                     # Presentación: rutas REST
│   │   ├── deps.py              # Sesión de BD, usuario actual y roles
│   │   ├── routes_auth.py
│   │   ├── routes_products.py
│   │   ├── routes_clients.py
│   │   ├── routes_sales.py
│   │   ├── routes_inventory.py
│   │   └── routes_reports.py
│   ├── schemas/                 # Modelos Pydantic (validación)
│   ├── services/                # Lógica de negocio
│   ├── repositories/            # Acceso a datos
│   ├── models/                  # Tablas SQLAlchemy
│   ├── database/                # Conexión (Singleton) y creación de la BD
│   └── patterns/                # Singleton y Observer
├── frontend/                    # HTML, CSS y JS
├── tests/
│   ├── unit/
│   ├── integration/
│   └── acceptance/
├── docs/                        # Documentación académica
├── data/                        # Aquí se crea papeleria.db (no se sube a Git)
├── .github/workflows/ci.yml     # Integración continua
├── pytest.ini
├── requirements.txt
├── LICENSE
└── README.md
```

## Instalación

```bash
git clone https://github.com/RolandBonilla/papeleria.git
cd papeleria
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows (PowerShell o CMD)
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear la base de datos con datos de prueba:

```bash
python -m app.database.init_db
```

Ejecutar la aplicación:

```bash
uvicorn app.main:app --reload
```

Abrir en el navegador:

- Aplicación: <http://127.0.0.1:8000>
- Documentación interactiva de la API (Swagger): <http://127.0.0.1:8000/docs>

Ejecutar las pruebas:

```bash
python -m pytest
```

## Usuarios de prueba

| Usuario | Contraseña | Rol |
| --- | --- | --- |
| `admin` | `admin123` | ADMINISTRADOR |
| `vendedor` | `vendedor123` | VENDEDOR |
| `inventario` | `inventario123` | INVENTARIO |

Son credenciales de demostración. Las contraseñas **no se guardan en texto plano**: `init_db` las convierte con PBKDF2-SHA256 (módulo `hashlib` de Python, sal aleatoria, 200 000 iteraciones) mediante `hash_password()` en `app/services/auth_service.py`. Para usar el sistema de verdad, cambie estas contraseñas y defina su propia clave con la variable de entorno `PAPELERIA_SECRET_KEY`.

Permisos por rol:

| Acción | ADMINISTRADOR | VENDEDOR | INVENTARIO |
| --- | :-: | :-: | :-: |
| Ver productos, inventario, alertas y clientes | Sí | Sí | Sí |
| Crear/editar/eliminar productos y categorías | Sí | No | Sí |
| Registrar ingreso de mercadería | Sí | No | Sí |
| Registrar ventas y ver reporte de ventas | Sí | Sí | No |
| Registrar y editar clientes | Sí | Sí | No |

## Variables de entorno (opcionales)

| Variable | Para qué sirve | Valor por defecto |
| --- | --- | --- |
| `PAPELERIA_DATABASE_URL` | Ubicación de la base de datos | `data/papeleria.db` |
| `PAPELERIA_SECRET_KEY` | Clave para firmar los tokens de sesión | clave de desarrollo local |
| `PAPELERIA_TOKEN_HOURS` | Duración de la sesión | 8 |

## Documentación

- [Requerimientos](docs/requirements.md)
- [Arquitectura](docs/architecture.md)
- [Pruebas](docs/testing.md)
- [API](docs/api.md)
- [Calidad ISO/IEC 25010](docs/iso25010.md)
- [Historias de usuario para Jira](docs/jira.md)

## Licencia

MIT. Ver [LICENSE](LICENSE).
