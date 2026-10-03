from sqlalchemy.orm import Session

from app.exceptions import DuplicateError, NotFoundError
from app.models.client import Client
from app.repositories.client_repository import ClientRepository
from app.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.clients = ClientRepository(db)

    def create(self, data: ClientCreate) -> Client:
        """RF-08: registrar cliente."""
        self._ensure_cedula_available(data.cedula)
        client = self.clients.add(Client(**data.model_dump()))
        self.db.commit()
        return client

    def get(self, client_id: int) -> Client:
        client = self.clients.get(client_id)
        if client is None:
            raise NotFoundError("Cliente no encontrado")
        return client

    def search(self, q: str | None = None) -> list[Client]:
        """RF-09: consultar clientes por cédula o nombre."""
        return self.clients.search(q)

    def update(self, client_id: int, data: ClientUpdate) -> Client:
        client = self.get(client_id)
        self._ensure_cedula_available(data.cedula, ignore_id=client_id)
        for field, value in data.model_dump().items():
            setattr(client, field, value)
        self.db.commit()
        return client

    def _ensure_cedula_available(self, cedula: str, ignore_id: int | None = None) -> None:
        existing = self.clients.get_by_cedula(cedula)
        if existing is not None and existing.id != ignore_id:
            raise DuplicateError(f"Ya existe un cliente con la cédula {cedula}")
