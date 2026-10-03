import pytest
from pydantic import ValidationError

from app.exceptions import DuplicateError, NotFoundError
from app.schemas.client import ClientCreate, ClientUpdate
from app.services.client_service import ClientService


def test_registrar_y_consultar_cliente(db):
    service = ClientService(db)
    client = service.create(ClientCreate(cedula="1712345678", name="Ana Mora", phone="0987654321", email="ana@example.com"))
    assert client.id is not None
    assert [c.cedula for c in service.search("Ana")] == ["1712345678"]
    assert [c.name for c in service.search("1712345678")] == ["Ana Mora"]


def test_cedula_duplicada_es_rechazada(db):
    with pytest.raises(DuplicateError):
        ClientService(db).create(ClientCreate(cedula="1700000001", name="Otro"))


@pytest.mark.parametrize("cedula", ["123", "12345678ab", "12345678901"])
def test_cedula_invalida_es_rechazada_por_el_esquema(cedula):
    with pytest.raises(ValidationError):
        ClientCreate(cedula=cedula, name="X")


def test_correo_invalido_es_rechazado():
    with pytest.raises(ValidationError):
        ClientCreate(cedula="1712345678", name="X", email="no-es-correo")


def test_editar_cliente(db):
    service = ClientService(db)
    cliente = service.search("María")[0]
    editado = service.update(cliente.id, ClientUpdate(cedula=cliente.cedula, name="María P. Pérez", phone="022345678"))
    assert editado.name == "María P. Pérez"
    assert editado.email is None


def test_cliente_inexistente(db):
    with pytest.raises(NotFoundError):
        ClientService(db).get(9999)


def test_busqueda_de_clientes_trata_comodines_como_texto(db):
    assert ClientService(db).search("%") == []
