from pydantic import BaseModel, Field
from decimal import Decimal


class AddCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class UpdateCartRequest(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemResponse(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(default=1, ge=1)
    model_config = {"from_attributes": True}


class CartItemDetailResponse(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    name: str
    price: Decimal = Field(gt=0)
    stock: int
