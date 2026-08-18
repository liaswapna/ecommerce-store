from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, Numeric, DateTime, String, ForeignKey, Enum
from app.database import Base
from decimal import Decimal
from datetime import datetime, timezone
from app.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), nullable=False)
    payment_intent_id: Mapped[str | None] = mapped_column(
        String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    items: Mapped[list["OrderItem"]] = relationship("OrderItem")


class OrderItem(Base):
    __tablename__ = "order_items"
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), primary_key=True, nullable=False)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id"), primary_key=True, nullable=False)
    name_at_purchase: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    price_at_purchase: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False)
