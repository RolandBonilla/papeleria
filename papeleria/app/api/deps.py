"""Dependencias compartidas por las rutas: sesión de base de datos, usuario actual y roles."""
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.connection import DatabaseManager
from app.exceptions import AuthenticationError, PermissionDeniedError
from app.models.user import Role, User
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = DatabaseManager().session_factory()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise AuthenticationError("Debe iniciar sesión")
    return AuthService(db).user_from_token(credentials.credentials)


def require_roles(*roles: Role):
    def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise PermissionDeniedError("Su rol no tiene permiso para esta acción")
        return user

    return checker


CurrentUser = Annotated[User, Depends(get_current_user)]
ManageProducts = Annotated[User, Depends(require_roles(Role.ADMINISTRADOR, Role.INVENTARIO))]
Sell = Annotated[User, Depends(require_roles(Role.ADMINISTRADOR, Role.VENDEDOR))]
