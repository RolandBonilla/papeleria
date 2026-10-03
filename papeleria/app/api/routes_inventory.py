from fastapi import APIRouter, Depends

from app.api.deps import DbSession, ManageProducts, get_current_user
from app.schemas.inventory import AlertOut, InventoryItemOut, StockEntryCreate
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory", tags=["Inventario"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[InventoryItemOut])
def list_inventory(db: DbSession, status: str | None = None):
    return InventoryService(db).list_inventory(status)


@router.get("/low-stock", response_model=list[InventoryItemOut])
def low_stock(db: DbSession):
    return InventoryService(db).low_stock_products()


@router.get("/alerts", response_model=list[AlertOut])
def open_alerts(db: DbSession):
    return InventoryService(db).open_alerts()


@router.post("/entries", response_model=InventoryItemOut, status_code=201)
def register_entry(data: StockEntryCreate, db: DbSession, user: ManageProducts):
    return InventoryService(db).register_entry(data.product_id, data.quantity, data.note, user.id)
