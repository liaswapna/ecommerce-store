from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import CreateProductRequest, UpdateProductRequest
from app.repositories.product import ProductRepository
from app.exceptions import NotFoundError, DatabaseError


class ProductService:
    def __init__(self):
        self.repository = ProductRepository()

    def get_all(self, db: Session, page: int, page_size: int, active_only: bool = True) -> list[Product]:
        return self.repository.get_all(db, page, page_size, active_only)

    def get_by_category(self, db: Session, category: str, page: int, page_size: int, active_only: bool = True) -> list[Product]:
        return self.repository.get_by_category(db, category, page, page_size, active_only)

    def get_by_id(self, db: Session, product_id: int) -> Product:
        product = self.repository.get_by_id(db, product_id)
        if product is None:
            raise NotFoundError("Product not found")
        return product

    def create(self, db: Session, data: CreateProductRequest) -> Product:
        try:
            return self.repository.create(db, data)
        except Exception:
            raise DatabaseError("Failed to create product")

    def update(self, db: Session, data: UpdateProductRequest, product_id: int) -> Product:
        try:
            product = self.repository.update(db, data, product_id)
        except Exception:
            raise DatabaseError("Failed to update product")
        if product is None:
            raise NotFoundError("Product not found")
        return product

    def delete(self, db: Session, product_id: int) -> Product:
        try:
            product = self.repository.delete(db, product_id)
        except Exception:
            raise DatabaseError("Failed to delete product")
        if product is None:
            raise NotFoundError("Product not found")
        return product
