"""Importar todos los modelos registra las tablas en ``Base.metadata``."""
from app.models.alert import Alert
from app.models.category import Category
from app.models.client import Client
from app.models.product import Product
from app.models.sale import Sale
from app.models.sale_detail import SaleDetail
from app.models.stock_movement import StockMovement
from app.models.user import Role, User

__all__ = [
    "Alert", "Category", "Client", "Product", "Role",
    "Sale", "SaleDetail", "StockMovement", "User",
]
