"""Conexión a la base de datos administrada con el patrón Singleton."""
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.patterns.singleton import SingletonMeta


def _enable_foreign_keys(dbapi_connection, _record) -> None:
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


class DatabaseManager(metaclass=SingletonMeta):
    """Única instancia responsable del motor y de las sesiones de la base de datos."""

    def __init__(self) -> None:
        self.database_url = settings.database_url
        self._prepare_sqlite_folder()
        self.engine = create_engine(
            self.database_url, connect_args={"check_same_thread": False}
        )
        event.listen(self.engine, "connect", _enable_foreign_keys)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def _prepare_sqlite_folder(self) -> None:
        prefix = "sqlite:///"
        if self.database_url.startswith(prefix) and ":memory:" not in self.database_url:
            Path(self.database_url[len(prefix):]).parent.mkdir(parents=True, exist_ok=True)
