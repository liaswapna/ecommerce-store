from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem
from app.enums import OrderStatus
from decimal import Decimal


class OrderRepository:
    def create_order(self, db: Session, user_id: int, total_price: Decimal) -> Order:
        order = Order(user_id=user_id, total_price=total_price,
                      status=OrderStatus.PENDING, payment_intent_id=None)
        db.add(order)
        db.flush()
        return order

    def create_order_items(self, db: Session, order_items: list[OrderItem]) -> None:
        db.add_all(order_items)
        db.flush()

    def get_orders(self, db: Session, user_id: int) -> list[Order]:
        return db.query(Order).filter(Order.user_id == user_id).all()

    def get_order_by_id(self, db: Session, order_id: int) -> Order | None:
        return db.query(Order).filter(Order.id == order_id).first()

    def update_order(self, db: Session, order_id: int, payment_intent_id: str | None = None, status: OrderStatus | None = None) -> Order | None:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order is None:
            return None
        if payment_intent_id is not None:
            order.payment_intent_id = payment_intent_id
        if status is not None:
            order.status = status
        db.commit()
        db.refresh(order)
        return order
