from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.client import Client


class ClientRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, client_id: int) -> Client | None:
        return self.db.get(Client, client_id)

    def get_by_cedula(self, cedula: str) -> Client | None:
        return self.db.scalar(select(Client).where(Client.cedula == cedula))

    def search(self, q: str | None = None) -> list[Client]:
        stmt = select(Client).order_by(Client.name)
        if q:
            stmt = stmt.where(or_(
                Client.cedula.icontains(q, autoescape=True),
                Client.name.icontains(q, autoescape=True),
            ))
        return list(self.db.scalars(stmt))

    def add(self, client: Client) -> Client:
        self.db.add(client)
        self.db.flush()
        return client
