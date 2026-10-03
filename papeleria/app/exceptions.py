"""Errores de negocio. La API los convierte en respuestas HTTP (ver app/main.py)."""


class BusinessError(Exception):
    status_code = 400


class InvalidDataError(BusinessError, ValueError):
    status_code = 422


class NotFoundError(BusinessError):
    status_code = 404


class DuplicateError(BusinessError):
    status_code = 409


class InsufficientStockError(BusinessError):
    status_code = 409


class AuthenticationError(BusinessError):
    status_code = 401


class PermissionDeniedError(BusinessError):
    status_code = 403
