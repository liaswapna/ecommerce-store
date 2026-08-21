from unittest.mock import MagicMock, patch
from decimal import Decimal
import pytest
from app.services.order import OrderService
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.cart import CartItemDetailResponse
from app.schemas.order import OrderDetailResponse, OrderSummaryResponse
from app.enums import OrderStatus
from app.exceptions import NotFoundError, OutOfStockError
from datetime import datetime, timezone


service = OrderService()


def make_product(**kwargs):
    defaults = dict(id=1, name="Nike Air Max", description="Running shoes",
                    image_url=None, category="shoes", price=Decimal("99.99"),
                    stock=50, is_active=True)
    defaults.update(kwargs)
    return Product(**defaults)


def make_cart_detail(**kwargs):
    defaults = dict(user_id=1, product_id=1, quantity=2,
                    name="Nike Air Max", price=Decimal("99.99"), stock=50)
    defaults.update(kwargs)
    return CartItemDetailResponse(**defaults)


def make_order(**kwargs):
    defaults = dict(id=1, user_id=1, total_price=Decimal("199.98"),
                    status=OrderStatus.PENDING, payment_intent_id=None,
                    created_at=datetime.now(timezone.utc), items=[])
    defaults.update(kwargs)
    order = MagicMock(spec=Order)
    for k, v in defaults.items():
        setattr(order, k, v)
    return order


def make_order_item(**kwargs):
    defaults = dict(order_id=1, product_id=1, name_at_purchase="Nike Air Max",
                    quantity=2, price_at_purchase=Decimal("99.99"))
    defaults.update(kwargs)
    item = MagicMock(spec=OrderItem)
    for k, v in defaults.items():
        setattr(item, k, v)
    return item


class TestPlaceOrder:

    def test_raises_not_found_when_cart_is_empty(self):
        # empty cart — should raise NotFoundError before any DB writes
        db = MagicMock()
        service.cart_repository.get_cart_details = MagicMock(return_value=[])
        with pytest.raises(NotFoundError):
            service.place_order(db, 1)

    def test_raises_not_found_when_product_missing(self):
        # product in cart no longer exists — should raise NotFoundError
        db = MagicMock()
        service.cart_repository.get_cart_details = MagicMock(return_value=[make_cart_detail()])
        service.product_repository.get_by_id = MagicMock(return_value=None)
        with pytest.raises(NotFoundError):
            service.place_order(db, 1)

    def test_raises_out_of_stock_when_stock_insufficient(self):
        # product stock is less than requested quantity — should raise OutOfStockError
        db = MagicMock()
        service.cart_repository.get_cart_details = MagicMock(return_value=[make_cart_detail(quantity=10)])
        service.product_repository.get_by_id = MagicMock(return_value=make_product(stock=5))
        with pytest.raises(OutOfStockError):
            service.place_order(db, 1)

    def test_success_returns_order_detail_response(self):
        # happy path — order created, stock decremented, cart cleared
        db = MagicMock()
        cart_items = [make_cart_detail(quantity=2)]
        product = make_product(stock=10)
        order = make_order()

        service.cart_repository.get_cart_details = MagicMock(return_value=cart_items)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.order_repository.create_order = MagicMock(return_value=order)
        service.order_repository.create_order_items = MagicMock()
        service.cart_repository.clear_cart = MagicMock()

        result = service.place_order(db, 1)

        assert isinstance(result, OrderDetailResponse)
        assert result.total_price == Decimal("199.98")
        assert result.status == OrderStatus.PENDING

    def test_rolls_back_on_db_error(self):
        # DB error during order creation — should rollback and re-raise
        db = MagicMock()
        cart_items = [make_cart_detail(quantity=2)]
        product = make_product(stock=10)

        service.cart_repository.get_cart_details = MagicMock(return_value=cart_items)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.order_repository.create_order = MagicMock(side_effect=Exception("DB error"))

        with pytest.raises(Exception):
            service.place_order(db, 1)

        db.rollback.assert_called_once()

    def test_calculates_total_price_correctly(self):
        # two items — total should be sum of price * quantity
        db = MagicMock()
        cart_items = [
            make_cart_detail(product_id=1, quantity=2, price=Decimal("99.99")),
            make_cart_detail(product_id=2, quantity=1, price=Decimal("49.99"))
        ]
        products = [make_product(id=1, price=Decimal("99.99"), stock=10),
                    make_product(id=2, price=Decimal("49.99"), stock=10)]
        order = make_order(total_price=Decimal("249.97"))

        service.cart_repository.get_cart_details = MagicMock(return_value=cart_items)
        service.product_repository.get_by_id = MagicMock(side_effect=products)
        service.order_repository.create_order = MagicMock(return_value=order)
        service.order_repository.create_order_items = MagicMock()
        service.cart_repository.clear_cart = MagicMock()

        result = service.place_order(db, 1)
        expected_total = Decimal("99.99") * 2 + Decimal("49.99") * 1
        service.order_repository.create_order.assert_called_once_with(db, 1, expected_total)


class TestGetOrders:

    def test_returns_list_of_order_summaries(self):
        # repository returns orders — service should convert to OrderSummaryResponse list
        db = MagicMock()
        orders = [make_order(), make_order(id=2)]
        service.order_repository.get_orders = MagicMock(return_value=orders)
        result = service.get_orders(db, 1)
        assert len(result) == 2
        assert all(isinstance(r, OrderSummaryResponse) for r in result)

    def test_returns_empty_list_when_no_orders(self):
        # no orders — should return empty list without error
        db = MagicMock()
        service.order_repository.get_orders = MagicMock(return_value=[])
        result = service.get_orders(db, 1)
        assert result == []


class TestGetOrderById:

    def test_raises_not_found_when_order_missing(self):
        # order doesn't exist — should raise NotFoundError
        db = MagicMock()
        service.order_repository.get_order_by_id = MagicMock(return_value=None)
        with pytest.raises(NotFoundError):
            service.get_order_by_id(db, 999)

    def test_returns_order_detail_with_items(self):
        # order exists with items — should return OrderDetailResponse with items list
        db = MagicMock()
        order_item = make_order_item()
        order = make_order(items=[order_item])
        service.order_repository.get_order_by_id = MagicMock(return_value=order)
        result = service.get_order_by_id(db, 1)
        assert isinstance(result, OrderDetailResponse)
        assert len(result.items) == 1
        assert result.items[0].name_at_purchase == "Nike Air Max"
