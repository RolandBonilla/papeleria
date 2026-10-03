"""Fixtures compartidas. Cada prueba usa una base SQLite en memoria nueva y aislada."""
import os

# Deben definirse ANTES de importar la aplicación: las pruebas nunca tocan la base real
# y usan pocas iteraciones de PBKDF2 para que sean rápidas.
os.environ["PAPELERIA_DATABASE_URL"] = "sqlite:///:memory:"
os.environ["PAPELERIA_PASSWORD_ITERATIONS"] = "1000"

from decimal import Decimal  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

import app.models  # noqa: E402,F401
from app.api.deps import get_db  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.database.init_db import seed_database  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories.product_repository import CategoryRepository  # noqa: E402
from app.schemas.product import ProductCreate  # noqa: E402
from app.services.product_service import ProductService  # noqa: E402


@pytest.fixture
def session_factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as seed_session:
        seed_database(seed_session)
    yield factory
    engine.dispose()


@pytest.fixture
def db(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory):
    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def _login(client, username, password):
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def admin_headers(client):
    return _login(client, "admin", "admin123")


@pytest.fixture
def vendedor_headers(client):
    return _login(client, "vendedor", "vendedor123")


@pytest.fixture
def inventario_headers(client):
    return _login(client, "inventario", "inventario123")


@pytest.fixture
def make_product(db):
    """Crea un producto de prueba en la categoría 'Papel' y lo devuelve."""
    def _make(code="TST001", name="Producto de prueba", price="2.50", stock=10, min_stock=2):
        category = CategoryRepository(db).get_by_name("Papel")
        return ProductService(db).create(ProductCreate(
            code=code, name=name, category_id=category.id,
            price=Decimal(price), stock=stock, min_stock=min_stock,
        ))
    return _make
