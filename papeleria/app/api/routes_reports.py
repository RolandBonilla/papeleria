from datetime import date

from fastapi import APIRouter, Depends

from app.api.deps import DbSession, Sell, get_current_user
from app.schemas.inventory import InventoryItemOut
from app.schemas.sale import DashboardOut, SalesReportOut
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["Reportes"])


@router.get("/sales", response_model=SalesReportOut)
def sales_report(db: DbSession, _user: Sell, date_from: date | None = None, date_to: date | None = None):
    return ReportService(db).sales_report(date_from, date_to)


@router.get("/low-stock", response_model=list[InventoryItemOut], dependencies=[Depends(get_current_user)])
def low_stock_report(db: DbSession):
    return ReportService(db).low_stock_report()


@router.get("/dashboard", response_model=DashboardOut, dependencies=[Depends(get_current_user)])
def dashboard(db: DbSession):
    return ReportService(db).dashboard()
