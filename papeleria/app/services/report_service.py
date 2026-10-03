from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.sale_repository import SaleRepository


def _sum_totals(sales) -> Decimal:
    return sum((sale.total for sale in sales), Decimal("0.00"))


class ReportService:
    def __init__(self, db: Session) -> None:
        self.sales = SaleRepository(db)
        self.products = ProductRepository(db)

    def sales_report(self, date_from: date | None = None, date_to: date | None = None) -> dict:
        """RF-11: ventas realizadas, con filtro opcional por fechas (ambas incluidas)."""
        start = datetime.combine(date_from, time.min) if date_from else None
        end = datetime.combine(date_to + timedelta(days=1), time.min) if date_to else None
        sales = self.sales.list(start, end)
        return {"sales": sales, "count": len(sales), "total": _sum_totals(sales)}

    def low_stock_report(self):
        """RF-12: productos con stock menor o igual al mínimo."""
        return self.products.list_low_stock()

    def dashboard(self) -> dict:
        today = datetime.combine(date.today(), time.min)
        sales_today = self.sales.list(today, today + timedelta(days=1))
        return {
            "total_products": len(self.products.search()),
            "low_stock_products": len(self.products.list_low_stock()),
            "sales_today": len(sales_today),
            "total_sold_today": _sum_totals(sales_today),
        }
