from datetime import date

from fastapi import APIRouter

from app.api.deps import DbSession, Sell
from app.exceptions import NotFoundError
from app.repositories.sale_repository import SaleRepository
from app.schemas.sale import SaleCreate, SaleOut
from app.services.report_service import ReportService
from app.services.sale_service import SaleService

router = APIRouter(prefix="/api", tags=["Ventas"])


@router.get("/sales", response_model=list[SaleOut])
def list_sales(db: DbSession, _user: Sell, date_from: date | None = None, date_to: date | None = None):
    return ReportService(db).sales_report(date_from, date_to)["sales"]


@router.post("/sales", response_model=SaleOut, status_code=201)
def create_sale(data: SaleCreate, db: DbSession, user: Sell):
    return SaleService(db).create_sale(data, user_id=user.id)


@router.get("/sales/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: DbSession, _user: Sell):
    sale = SaleRepository(db).get(sale_id)
    if sale is None:
        raise NotFoundError("Venta no encontrada")
    return sale
