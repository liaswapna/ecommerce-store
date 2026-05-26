from sqlalchemy.orm import Session
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemDetailResponse, AddCartRequest, UpdateCartRequest


class CartRepository:
    def get_cart_details(self, db: Session, user_id: int) -> list[CartItemDetailResponse]:
        cart_details = db.query(CartItem, Product).join(
            Product, CartItem.product_id == Product.id).filter(CartItem.user_id == user_id).all()
        return [
            CartItemDetailResponse(
                user_id=cart_item.user_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                name=product.name,
                price=product.price
            )
            for cart_item, product in cart_details
        ]

    def add_to_cart(self, db: Session, user_id: int, data: AddCartRequest) -> CartItem:
        cart_item = CartItem(
            user_id=user_id,
            product_id=data.product_id,
            quantity=data.quantity
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item

    def update_cart(self, db: Session, user_id: int, data: UpdateCartRequest) -> CartItem | None:
        cart_item = db.query(CartItem).filter(CartItem.user_id == user_id,
                                              CartItem.product_id == data.product_id).first()
        if cart_item is None:
            return None
        cart_item.quantity = data.quantity
        db.commit()
        db.refresh(cart_item)
        return cart_item

    def delete_from_cart(self, db: Session, user_id: int, product_id: int) -> CartItem | None:
        cart_item = db.query(CartItem).filter(
            CartItem.user_id == user_id, CartItem.product_id == product_id).first()
        if cart_item is None:
            return None
        db.delete(cart_item)
        db.commit()
        return cart_item

    def clear_cart(self, db: Session, user_id: int) -> None:
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()
        return
