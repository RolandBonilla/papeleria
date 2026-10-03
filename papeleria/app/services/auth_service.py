"""Autenticación: contraseñas con PBKDF2 (hashlib) y tokens firmados con HMAC (hashlib/hmac)."""
import base64
import hashlib
import hmac
import json
import secrets
import time

from sqlalchemy.orm import Session

from app.config import settings
from app.exceptions import AuthenticationError
from app.models.user import User
from app.repositories.user_repository import UserRepository

ALGORITHM = "pbkdf2_sha256"


def _derive(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations).hex()


def hash_password(password: str, iterations: int | None = None) -> str:
    """Devuelve ``pbkdf2_sha256$iteraciones$sal$hash``. La sal es aleatoria para cada contraseña."""
    iterations = iterations or settings.password_iterations
    salt = secrets.token_hex(16)
    return f"{ALGORITHM}${iterations}${salt}${_derive(password, salt, iterations)}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored_hash.split("$")
        if algorithm != ALGORITHM:
            return False
        return hmac.compare_digest(_derive(password, salt, int(iterations)), digest)
    except ValueError:
        return False


def _sign(body: str) -> str:
    return hmac.new(settings.secret_key.encode(), body.encode(), hashlib.sha256).hexdigest()


def create_token(user_id: int, now: float | None = None) -> str:
    expires = int((now if now is not None else time.time()) + settings.token_hours * 3600)
    body = base64.urlsafe_b64encode(json.dumps({"uid": user_id, "exp": expires}).encode()).decode()
    return f"{body}.{_sign(body)}"


def read_token(token: str, now: float | None = None) -> int:
    """Valida firma y vencimiento; devuelve el id del usuario."""
    try:
        body, signature = token.split(".")
        if not hmac.compare_digest(signature, _sign(body)):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(body.encode()))
        if payload["exp"] < (now if now is not None else time.time()):
            raise AuthenticationError("La sesión expiró, inicie sesión nuevamente")
        return int(payload["uid"])
    except AuthenticationError:
        raise
    except (ValueError, KeyError, TypeError):
        raise AuthenticationError("Token inválido") from None


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def login(self, username: str, password: str) -> dict:
        user = self.users.get_by_username(username.strip())
        if user is None or not user.active or not verify_password(password, user.password_hash):
            raise AuthenticationError("Usuario o contraseña incorrectos")
        return {
            "access_token": create_token(user.id),
            "token_type": "bearer",
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        }

    def user_from_token(self, token: str) -> User:
        user = self.users.get(read_token(token))
        if user is None or not user.active:
            raise AuthenticationError("Usuario no válido")
        return user
