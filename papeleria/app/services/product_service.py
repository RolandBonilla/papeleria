from sqlalchemy.orm import Session

from app.exceptions import DuplicateError, NotFoundError
from app.models.category import Category
from app.models.product import Product
from app.models.stock_movement import MOVEMENT_INITIAL
from app.repositories.product_repository import CategoryRepository, ProductRepository
from app.schemas.product import CategoryCreate, ProductCreate, ProductUpdate
from app.services.inventory_service import InventoryService


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.products = ProductRepository(db)
        self.categories = CategoryRepository(db)
        self.inventory = InventoryService(db)

    def create(self, data: ProductCreate) -> Product:
        """RF-01: registrar producto."""
        self._ensure_category(data.category_id)
        self._ensure_code_available(data.code)
        product = self.products.add(Product(
            code=data.code, name=data.name, category_id=data.category_id,
            price=data.price, min_stock=data.min_stock, stock=0,
        ))
        if data.stock > 0:
            self.inventory.apply_movement(product, data.stock, MOVEMENT_INITIAL, reference="Stock inicial")
        else:
            self.inventory.notify_stock_changed(product)
        self.db.commit()
        return product

    def get(self, product_id: int) -> Product:
        product = self.products.get(product_id)
        if product is None or not product.active:
            raise NotFoundError("Producto no encontrado")
        return product

    def search(self, **filters) -> list[Product]:
        """RF-02: buscar por código, nombre o categoría."""
        return self.products.search(**filters)

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        """RF-03: actualizar datos del producto."""
        product = self.get(product_id)
        self._ensure_category(data.category_id)
        self._ensure_code_available(data.code, ignore_id=product_id)
        product.code = data.code
        product.name = data.name
        product.category_id = data.category_id
        product.price = data.price
        product.min_stock = data.min_stock
        self.db.flush()
        self.db.refresh(product)
        self.inventory.notify_stock_changed(product)
        self.db.commit()
        return product

    def delete(self, product_id: int) -> None:
        """Baja lógica: el producto deja de mostrarse pero se conserva el historial de ventas."""
        product = self.get(product_id)
        product.active = False
        self.inventory.notify_stock_changed(product)
        self.db.commit()

    def list_categories(self) -> list[Category]:
        return self.categories.list()

    def create_category(self, data: CategoryCreate) -> Category:
        if self.categories.get_by_name(data.name):
            raise DuplicateError("La categoría ya existe")
        category = self.categories.add(Category(name=data.name))
        self.db.commit()
        return category

    def _ensure_category(self, category_id: int) -> None:
        if self.categories.get(category_id) is None:
            raise NotFoundError("La categoría indicada no existe")

    def _ensure_code_available(self, code: str, ignore_id: int | None = None) -> None:
        existing = self.products.get_by_code(code)
        if existing is not None and existing.id != ignore_id:
            raise DuplicateError(f"Ya existe un producto con el código {code}")
