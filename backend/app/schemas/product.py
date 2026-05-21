from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal


class CreateProductRequest(BaseModel):
    name: str
    description: str
    image_url: str | None = None
    category: str
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    is_active: bool = True


class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
    category: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    image_url: str | None
    category: str
    price: Decimal
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
