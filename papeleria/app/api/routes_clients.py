from fastapi import APIRouter, Depends

from app.api.deps import DbSession, Sell, get_current_user
from app.schemas.client import ClientCreate, ClientOut, ClientUpdate
from app.services.client_service import ClientService

router = APIRouter(prefix="/api", tags=["Clientes"])
authenticated = [Depends(get_current_user)]


@router.get("/clients", response_model=list[ClientOut], dependencies=authenticated)
def list_clients(db: DbSession, q: str | None = None):
    return ClientService(db).search(q)


@router.post("/clients", response_model=ClientOut, status_code=201)
def create_client(data: ClientCreate, db: DbSession, _user: Sell):
    return ClientService(db).create(data)


@router.get("/clients/{client_id}", response_model=ClientOut, dependencies=authenticated)
def get_client(client_id: int, db: DbSession):
    return ClientService(db).get(client_id)


@router.put("/clients/{client_id}", response_model=ClientOut)
def update_client(client_id: int, data: ClientUpdate, db: DbSession, _user: Sell):
    return ClientService(db).update(client_id, data)
