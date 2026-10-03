import pytest

from app.exceptions import AuthenticationError
from app.services.auth_service import (AuthService, create_token, hash_password, read_token,
                                       verify_password)


def test_hash_no_guarda_la_contraseña_y_se_puede_verificar():
    stored = hash_password("secreto123")
    assert "secreto123" not in stored
    assert verify_password("secreto123", stored)
    assert not verify_password("otra", stored)


def test_misma_contraseña_genera_hashes_distintos():
    assert hash_password("abc") != hash_password("abc")


def test_hash_con_formato_invalido_no_verifica():
    assert not verify_password("abc", "texto-sin-formato")


def test_token_valido_devuelve_el_usuario():
    assert read_token(create_token(7)) == 7


def test_token_manipulado_es_rechazado():
    token = create_token(7)
    with pytest.raises(AuthenticationError):
        read_token(token[:-2] + "00")


def test_token_vencido_es_rechazado():
    token = create_token(7, now=0)
    with pytest.raises(AuthenticationError):
        read_token(token)


def test_login_correcto_e_incorrecto(db):
    service = AuthService(db)
    assert service.login("admin", "admin123")["role"] == "ADMINISTRADOR"
    with pytest.raises(AuthenticationError):
        service.login("admin", "mala")
    with pytest.raises(AuthenticationError):
        service.login("no-existe", "admin123")
