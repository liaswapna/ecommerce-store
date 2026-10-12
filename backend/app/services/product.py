import logging
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import CreateProductRequest, UpdateProductRequest
from app.repositories.product import ProductRepository
from app.exceptions import NotFoundError, DatabaseError
from app.embedder import Embedder

logger = logging.getLogger(__name__)

SEARCH_LIMIT = 5


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

    def create(self, db: Session, data: CreateProductRequest, embedder: Embedder | None = None) -> Product:
        try:
            product = self.repository.create(db, data)
        except Exception:
            raise DatabaseError("Failed to create product")
        self._save_embedding(db, product, embedder)
        return product

    def update(self, db: Session, data: UpdateProductRequest, product_id: int, embedder: Embedder | None = None) -> Product:
        try:
            product = self.repository.update(db, data, product_id)
        except Exception:
            raise DatabaseError("Failed to update product")
        if product is None:
            raise NotFoundError("Product not found")
        text_changed = any(value is not None for value in (data.name, data.description, data.category))
        if text_changed or product.embedding is None:
            self._save_embedding(db, product, embedder)
        return product

    def search(self, db: Session, query: str, embedder: Embedder | None = None, limit: int = SEARCH_LIMIT) -> list[Product]:
        query = query.strip()
        if not query:
            return []
        if embedder is not None:
            try:
                query_embedding = embedder.embed([query])[0]
                results = self.repository.search_by_embedding(db, query_embedding, limit)
                if results:
                    return results
            except Exception:
                db.rollback()
                logger.warning("Semantic search failed for %r; using keyword search", query)
        return self.repository.search_by_keyword(db, query, limit)

    def delete(self, db: Session, product_id: int) -> Product:
        try:
            product = self.repository.delete(db, product_id)
        except Exception:
            raise DatabaseError("Failed to delete product")
        if product is None:
            raise NotFoundError("Product not found")
        return product

    @staticmethod
    def product_text(product: Product) -> str:
        return f"{product.name}. {product.description}. Category: {product.category}"

    def _save_embedding(self, db: Session, product: Product, embedder: Embedder | None) -> None:
        if embedder is None:
            return
        try:
            embedding = embedder.embed([self.product_text(product)])[0]
            self.repository.update_embedding(db, product, embedding)
        except Exception:
            db.rollback()
            logger.warning("Could not embed product %s; saved without embedding", product.id)
