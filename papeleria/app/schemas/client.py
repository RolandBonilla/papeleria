from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ClientName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class ClientBase(BaseModel):
    cedula: str = Field(pattern=r"^\d{10}$", description="10 dígitos")
    name: ClientName
    phone: str | None = Field(default=None, pattern=r"^\+?\d{7,15}$")
    email: str | None = Field(default=None, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
