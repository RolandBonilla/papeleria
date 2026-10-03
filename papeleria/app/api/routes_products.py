from fastapi import APIRouter, Depends, Response

from app.api.deps import DbSession, ManageProducts, get_current_user
from app.schemas.product import CategoryCreate, CategoryOut, ProductCreate, ProductOut, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/api", tags=["Productos"])
authenticated = [Depends(get_current_user)]


@router.get("/products", response_model=list[ProductOut], dependencies=authenticated)
def list_products(db: DbSession, q: str | None = None, code: str | None = None,
                  name: str | None = None, category_id: int | None = None):
    return ProductService(db).search(q=q, code=code, name=name, category_id=category_id)


@router.post("/products", response_model=ProductOut, status_code=201)
def create_product(data: ProductCreate, db: DbSession, _user: ManageProducts):
    return ProductService(db).create(data)


@router.get("/products/{product_id}", response_model=ProductOut, dependencies=authenticated)
def get_product(product_id: int, db: DbSession):
    return ProductService(db).get(product_id)


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: DbSession, _user: ManageProducts):
    return ProductService(db).update(product_id, data)


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: DbSession, _user: ManageProducts):
    ProductService(db).delete(product_id)
    return Response(status_code=204)


@router.get("/categories", response_model=list[CategoryOut], dependencies=authenticated)
def list_categories(db: DbSession):
    return ProductService(db).list_categories()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryCreate, db: DbSession, _user: ManageProducts):
    return ProductService(db).create_category(data)
