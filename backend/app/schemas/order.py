from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from app.enums import OrderStatus


class OrderSummaryResponse(BaseModel):
    order_id: int = Field(alias="id")
    total_price: Decimal = Field(gt=0)
    status: OrderStatus
    created_at: datetime
    model_config = {"from_attributes": True, "populate_by_name": True}


class OrderItemSchema(BaseModel):
    product_id: int
    name_at_purchase: str
    quantity: int
    price_at_purchase: Decimal = Field(gt=0)
    model_config = {"from_attributes": True}


class OrderDetailResponse(BaseModel):
    order_id: int = Field(alias="id")
    total_price: Decimal = Field(gt=0)
    status: OrderStatus
    created_at: datetime
    items: list[OrderItemSchema]
    model_config = {"from_attributes": True, "populate_by_name": True}
