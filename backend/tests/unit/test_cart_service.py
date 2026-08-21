from unittest.mock import MagicMock
from decimal import Decimal
import pytest
from app.services.cart import CartService
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemDetailResponse
from app.exceptions import NotFoundError, OutOfStockError, DatabaseError


service = CartService()


def make_product(**kwargs):
    # helper to create a Product object with sensible defaults — override any field via kwargs
    defaults = dict(id=1, name="Nike Air Max", description="Running shoes",
                    image_url=None, category="shoes", price=Decimal("99.99"),
                    stock=50, is_active=True)
    defaults.update(kwargs)
    return Product(**defaults)


def make_cart_item(**kwargs):
    # helper to create a CartItem object with sensible defaults — override any field via kwargs
    defaults = dict(user_id=1, product_id=1, quantity=2)
    defaults.update(kwargs)
    return CartItem(**defaults)


def make_cart_detail(**kwargs):
    defaults = dict(user_id=1, product_id=1, quantity=2,
                    name="Nike Air Max", price=Decimal("99.99"), stock=50)
    defaults.update(kwargs)
    return CartItemDetailResponse(**defaults)


class TestGetCartDetails:

    def test_returns_list_of_cart_items(self):
        # repository returns cart items with product details — service should pass them back
        db = MagicMock()
        items = [make_cart_detail(), make_cart_detail(product_id=2)]
        service.cart_repository.get_cart_details = MagicMock(return_value=items)
        result = service.get_cart_details(db, 1)
        assert len(result) == 2

    def test_returns_empty_list_when_cart_is_empty(self):
        # repository returns [] — service should return [] without error
        db = MagicMock()
        service.cart_repository.get_cart_details = MagicMock(return_value=[])
        result = service.get_cart_details(db, 1)
        assert result == []


class TestAddToCart:

    def test_success(self):
        # product exists with enough stock — service should return the created cart item
        db = MagicMock()
        product = make_product(stock=10)
        cart_item = make_cart_item(quantity=2)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.add_to_cart = MagicMock(return_value=cart_item)
        data = MagicMock(product_id=1, quantity=2)
        result = service.add_to_cart(db, 1, data)
        assert result.quantity == 2

    def test_raises_not_found_when_product_missing(self):
        # product doesn't exist — service should raise NotFoundError before touching cart
        db = MagicMock()
        service.product_repository.get_by_id = MagicMock(return_value=None)
        data = MagicMock(product_id=999, quantity=1)
        with pytest.raises(NotFoundError):
            service.add_to_cart(db, 1, data)

    def test_raises_out_of_stock_when_stock_insufficient(self):
        # product stock is less than requested quantity — service should raise OutOfStockError
        db = MagicMock()
        product = make_product(stock=1)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        data = MagicMock(product_id=1, quantity=5)
        with pytest.raises(OutOfStockError):
            service.add_to_cart(db, 1, data)

    def test_raises_database_error_on_failure(self):
        # repository raises exception — service should wrap it in DatabaseError
        db = MagicMock()
        product = make_product(stock=10)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.add_to_cart = MagicMock(side_effect=Exception("DB error"))
        data = MagicMock(product_id=1, quantity=2)
        with pytest.raises(DatabaseError):
            service.add_to_cart(db, 1, data)


class TestUpdateCart:

    def test_success(self):
        # product exists, stock sufficient, cart item exists — service should return updated item
        db = MagicMock()
        product = make_product(stock=10)
        cart_item = make_cart_item(quantity=3)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.update_cart = MagicMock(return_value=cart_item)
        data = MagicMock(product_id=1, quantity=3)
        result = service.update_cart(db, 1, data)
        assert result.quantity == 3

    def test_raises_not_found_when_product_missing(self):
        # product doesn't exist — NotFoundError before touching cart
        db = MagicMock()
        service.product_repository.get_by_id = MagicMock(return_value=None)
        data = MagicMock(product_id=999, quantity=1)
        with pytest.raises(NotFoundError):
            service.update_cart(db, 1, data)

    def test_raises_out_of_stock_when_stock_insufficient(self):
        # product stock is less than requested quantity — OutOfStockError
        db = MagicMock()
        product = make_product(stock=1)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        data = MagicMock(product_id=1, quantity=5)
        with pytest.raises(OutOfStockError):
            service.update_cart(db, 1, data)

    def test_raises_not_found_when_cart_item_missing(self):
        # product exists but this item isn't in the cart — NotFoundError
        db = MagicMock()
        product = make_product(stock=10)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.update_cart = MagicMock(return_value=None)
        data = MagicMock(product_id=1, quantity=2)
        with pytest.raises(NotFoundError):
            service.update_cart(db, 1, data)

    def test_raises_database_error_on_failure(self):
        # repository raises exception — service should wrap it in DatabaseError
        db = MagicMock()
        product = make_product(stock=10)
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.update_cart = MagicMock(side_effect=Exception("DB error"))
        data = MagicMock(product_id=1, quantity=2)
        with pytest.raises(DatabaseError):
            service.update_cart(db, 1, data)


class TestDeleteFromCart:

    def test_success(self):
        # product exists, cart item exists — service should return the deleted item
        db = MagicMock()
        product = make_product()
        cart_item = make_cart_item()
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.delete_from_cart = MagicMock(return_value=cart_item)
        result = service.delete_from_cart(db, 1, 1)
        assert result.product_id == 1

    def test_raises_not_found_when_product_missing(self):
        # product doesn't exist — NotFoundError before touching cart
        db = MagicMock()
        service.product_repository.get_by_id = MagicMock(return_value=None)
        with pytest.raises(NotFoundError):
            service.delete_from_cart(db, 1, 999)

    def test_raises_not_found_when_cart_item_missing(self):
        # product exists but item not in cart — NotFoundError
        db = MagicMock()
        product = make_product()
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.delete_from_cart = MagicMock(return_value=None)
        with pytest.raises(NotFoundError):
            service.delete_from_cart(db, 1, 1)

    def test_raises_database_error_on_failure(self):
        # repository raises exception — service should wrap it in DatabaseError
        db = MagicMock()
        product = make_product()
        service.product_repository.get_by_id = MagicMock(return_value=product)
        service.cart_repository.delete_from_cart = MagicMock(side_effect=Exception("DB error"))
        with pytest.raises(DatabaseError):
            service.delete_from_cart(db, 1, 1)


class TestClearCart:

    def test_success(self):
        # repository clears cart — service should complete without error
        db = MagicMock()
        service.cart_repository.clear_cart = MagicMock(return_value=None)
        result = service.clear_cart(db, 1)
        assert result is None

    def test_raises_database_error_on_failure(self):
        # repository raises exception — service should wrap it in DatabaseError
        db = MagicMock()
        service.cart_repository.clear_cart = MagicMock(side_effect=Exception("DB error"))
        with pytest.raises(DatabaseError):
            service.clear_cart(db, 1)
