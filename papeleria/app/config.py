"""Configuración central. Los valores pueden cambiarse con variables de entorno."""
import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    token_hours: int
    password_iterations: int


def load_settings() -> Settings:
    default_db = f"sqlite:///{(BASE_DIR / 'data' / 'papeleria.db').as_posix()}"
    return Settings(
        database_url=os.getenv("PAPELERIA_DATABASE_URL", default_db),
        # Clave solo para desarrollo local. En un uso real debe definirse PAPELERIA_SECRET_KEY.
        secret_key=os.getenv("PAPELERIA_SECRET_KEY", "clave-de-desarrollo-local"),
        token_hours=int(os.getenv("PAPELERIA_TOKEN_HOURS", "8")),
        password_iterations=int(os.getenv("PAPELERIA_PASSWORD_ITERATIONS", "200000")),
    )


settings = load_settings()
