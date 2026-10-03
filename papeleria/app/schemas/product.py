from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Code = Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=1, max_length=30)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class ProductBase(BaseModel):
    code: Code
    name: Name
    category_id: int
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    min_stock: int = Field(ge=0)


class ProductCreate(ProductBase):
    stock: int = Field(default=0, ge=0)


class ProductUpdate(ProductBase):
    """El stock no se edita aquí: cambia solo con ingresos y ventas (queda trazabilidad)."""


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock: int
    active: bool
    category_name: str


class CategoryCreate(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]


class CategoryOut(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
