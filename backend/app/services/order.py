from sqlalchemy.orm import Session
from app.repositories.cart import CartRepository
from app.repositories.product import ProductRepository
from app.repositories.order import OrderRepository
from app.schemas.order import OrderDetailResponse, OrderItemSchema, OrderSummaryResponse
from app.schemas.cart import CartItemDetailResponse
from app.exceptions import NotFoundError, OutOfStockError
from app.models.product import Product
from app.models.order import Order, OrderItem
from decimal import Decimal
import logging
logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self):
        self.cart_repository = CartRepository()
        self.product_repository = ProductRepository()
        self.order_repository = OrderRepository()

    def place_order(self, db: Session, user_id: int) -> OrderDetailResponse:
        # get the product and cart details
        cart_details: list[CartItemDetailResponse] = self.cart_repository.get_cart_details(
            db, user_id)
        if not cart_details:
            raise NotFoundError("Cart is empty")

        # check the stock in product
        # calculate the total price
        total_price: Decimal = Decimal("0.00")
        products: list[Product] = []
        for item in cart_details:
            product: Product = self.product_repository.get_by_id(
                db, item.product_id)
            if product is None:
                raise NotFoundError("Product Not Found")
            if product.stock < item.quantity:
                raise OutOfStockError(" Out of Stock")
            total_price += item.quantity * product.price
            products.append(product)

        # create the order in the db
        # get the order id and create the list of order items
        # create the order items in the orderItems table
        # reduce the quantity from product
        try:
            order: Order = self.order_repository.create_order(
                db, user_id, total_price)
            order_items = []
            for item, product in zip(cart_details, products):
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    name_at_purchase=product.name,
                    quantity=item.quantity,
                    price_at_purchase=product.price
                )
                order_items.append(order_item)
                product.stock -= item.quantity
            self.order_repository.create_order_items(db, order_items)
            db.commit()
        except Exception:
            db.rollback()
            raise
        # TODO:
        # call the stripe API
        # if successfull delete the cart items
        # if not successfull no change with cart items and increase the quantity in the product
        try:
            self.cart_repository.clear_cart(db, user_id)
            db.commit()
        except Exception:
            logger.error(f"Failed to clear cart for user {user_id}")
        return OrderDetailResponse(
            order_id=order.id,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
            items=[OrderItemSchema(product_id=order_item.product_id, name_at_purchase=order_item.name_at_purchase,
                                   quantity=order_item.quantity, price_at_purchase=order_item.price_at_purchase) for order_item in order_items]
        )

    def get_orders(self, db: Session, user_id: int) -> list[OrderSummaryResponse]:
        orders = self.order_repository.get_orders(db, user_id)
        return [OrderSummaryResponse(id=order.id, total_price=order.total_price, status=order.status, created_at=order.created_at) for order in orders]

    def get_order_by_id(self, db: Session, order_id: int) -> OrderDetailResponse:
        order = self.order_repository.get_order_by_id(db, order_id)
        if order is None:
            raise NotFoundError("Order not found")
        return OrderDetailResponse(
            order_id=order.id,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
            items=[OrderItemSchema.model_validate(
                item) for item in order.items]
        )
