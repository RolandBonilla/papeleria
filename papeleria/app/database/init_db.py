"""Crea las tablas y carga datos iniciales. Uso: ``python -m app.database.init_db``."""
from decimal import Decimal

from sqlalchemy import Engine
from sqlalchemy.orm import Session

import app.models  # noqa: F401  (registra las tablas)
from app.database.base import Base
from app.database.connection import DatabaseManager
from app.models.category import Category
from app.models.client import Client
from app.models.user import Role, User
from app.repositories.user_repository import UserRepository
from app.schemas.product import ProductCreate
from app.services.auth_service import hash_password
from app.services.product_service import ProductService

# Credenciales de prueba (se guardan con hash PBKDF2, nunca en texto plano en la base).
DEMO_USERS = [
    ("admin", "admin123", "Administrador", Role.ADMINISTRADOR),
    ("vendedor", "vendedor123", "Vendedor", Role.VENDEDOR),
    ("inventario", "inventario123", "Encargado de inventario", Role.INVENTARIO),
]
DEMO_CATEGORIES = ["Cuadernos", "Escritura", "Carpetas", "Papel"]
DEMO_PRODUCTS = [
    ("PAP001", "Cuaderno universitario", "Cuadernos", "2.50", 20, 5),
    ("PAP002", "Esferográfico azul", "Escritura", "0.50", 50, 10),
    ("PAP003", "Carpeta manila", "Carpetas", "0.75", 8, 5),
    ("PAP004", "Resma de papel A4", "Papel", "5.50", 3, 5),
]
DEMO_CLIENTS = [
    ("1700000001", "María Pérez", "0991234567", "maria@example.com"),
    ("1700000002", "Juan Torres", None, None),
]


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def seed_database(db: Session) -> bool:
    """Carga los datos de prueba solo si la base está vacía. Devuelve True si cargó datos."""
    if UserRepository(db).count() > 0:
        return False

    for username, password, full_name, role in DEMO_USERS:
        db.add(User(username=username, password_hash=hash_password(password),
                    full_name=full_name, role=role.value))
    categories = {name: Category(name=name) for name in DEMO_CATEGORIES}
    db.add_all(categories.values())
    db.add_all(Client(cedula=c, name=n, phone=p, email=e) for c, n, p, e in DEMO_CLIENTS)
    db.commit()

    products = ProductService(db)
    for code, name, category, price, stock, min_stock in DEMO_PRODUCTS:
        products.create(ProductCreate(
            code=code, name=name, category_id=categories[category].id,
            price=Decimal(price), stock=stock, min_stock=min_stock,
        ))
    return True


def init_database() -> bool:
    manager = DatabaseManager()
    create_tables(manager.engine)
    with manager.session_factory() as db:
        return seed_database(db)


if __name__ == "__main__":
    seeded = init_database()
    print("Base de datos creada con datos de prueba." if seeded else "La base de datos ya tenía datos; no se modificó.")
