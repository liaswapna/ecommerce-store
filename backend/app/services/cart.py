from sqlalchemy.orm import Session
from app.repositories.cart import CartRepository
from app.repositories.product import ProductRepository
from app.schemas.cart import AddCartRequest, UpdateCartRequest, CartItemResponse, CartItemDetailResponse
from app.exceptions import NotFoundError, OutOfStockError, DatabaseError
from app.models.product import Product


class CartService:
    def __init__(self):
        self.cart_repository = CartRepository()
        self.product_repository = ProductRepository()

    def _get_product(self, db: Session, product_id: int) -> Product:
        # DB crash on reads handled globally in main.py
        product = self.product_repository.get_by_id(db, product_id)
        if product is None:
            raise NotFoundError("Product not found")
        return product

    def get_cart_details(self, db: Session, user_id: int) -> list[CartItemDetailResponse]:
        return self.cart_repository.get_cart_details(db, user_id)

    def add_to_cart(self, db: Session, user_id: int, data: AddCartRequest) -> CartItemResponse:
        product = self._get_product(db, data.product_id)
        if product.stock < data.quantity:
            raise OutOfStockError("Product out of stock")
        try:
            cart_details = self.cart_repository.add_to_cart(db, user_id, data)
        except Exception:
            raise DatabaseError("Failed to add into cart")
        return cart_details

    def update_cart(self, db: Session, user_id: int, data: UpdateCartRequest) -> CartItemResponse:
        product = self._get_product(db, data.product_id)
        if product.stock < data.quantity:
            raise OutOfStockError("Product out of stock")
        try:
            cart_details = self.cart_repository.update_cart(db, user_id, data)
        except Exception:
            raise DatabaseError("Failed to update cart")
        if cart_details is None:
            raise NotFoundError("Cart item not found")
        return cart_details

    def delete_from_cart(self, db: Session, user_id: int, product_id: int) -> CartItemResponse:
        self._get_product(db, product_id)
        try:
            cart_details = self.cart_repository.delete_from_cart(
                db, user_id, product_id)
        except Exception:
            raise DatabaseError("Failed to delete from cart")
        if cart_details is None:
            raise NotFoundError("Cart item not found")
        return cart_details

    def clear_cart(self, db: Session, user_id: int) -> None:
        try:
            self.cart_repository.clear_cart(
                db, user_id)
        except Exception:
            raise DatabaseError("Failed to clear the cart")
        return
