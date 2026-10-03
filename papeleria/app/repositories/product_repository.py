from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, product_id: int) -> Product | None:
        return self.db.get(Product, product_id)

    def get_by_code(self, code: str) -> Product | None:
        return self.db.scalar(select(Product).where(Product.code == code))

    def search(self, *, q=None, code=None, name=None, category_id=None) -> list[Product]:
        stmt = select(Product).where(Product.active.is_(True)).order_by(Product.name)
        if q:
            stmt = stmt.where(or_(
                Product.code.icontains(q, autoescape=True),
                Product.name.icontains(q, autoescape=True),
            ))
        if code:
            stmt = stmt.where(Product.code.icontains(code, autoescape=True))
        if name:
            stmt = stmt.where(Product.name.icontains(name, autoescape=True))
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        return list(self.db.scalars(stmt))

    def list_low_stock(self) -> list[Product]:
        stmt = (
            select(Product)
            .where(Product.active.is_(True), Product.stock <= Product.min_stock)
            .order_by(Product.stock, Product.name)
        )
        return list(self.db.scalars(stmt))

    def add(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        return product


class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        """Busca por nombre exacto sin distinguir mayúsculas (los símbolos % y _ son texto normal)."""
        wanted = name.casefold()
        return next((c for c in self.list() if c.name.casefold() == wanted), None)

    def list(self) -> list[Category]:
        return list(self.db.scalars(select(Category).order_by(Category.name)))

    def add(self, category: Category) -> Category:
        self.db.add(category)
        self.db.flush()
        return category
