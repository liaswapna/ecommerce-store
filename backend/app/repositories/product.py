from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import CreateProductRequest, UpdateProductRequest


class ProductRepository:

    # active_only=True → active products only (customers), False → all products including inactive (admin)
    def get_all(self, db: Session, page: int, page_size: int, active_only: bool = True) -> list[Product]:
        skip = (page - 1) * page_size
        if active_only:
            return db.query(Product).filter(Product.is_active == True).offset(skip).limit(page_size).all()
        return db.query(Product).offset(skip).limit(page_size).all()

    # active_only=True → active products only (customers), False → all products including inactive (admin)
    def get_by_category(self, db: Session, category: str, page: int, page_size: int, active_only: bool = True) -> list[Product]:
        skip = (page - 1) * page_size
        if active_only:
            return db.query(Product).filter(Product.category == category, Product.is_active == True).offset(skip).limit(page_size).all()
        return db.query(Product).filter(Product.category == category).offset(skip).limit(page_size).all()

    def get_by_id(self, db: Session, product_id: int) -> Product | None:
        return db.query(Product).filter(Product.id == product_id).first()

    def create(self, db: Session, data: CreateProductRequest) -> Product:
        product = Product(
            name=data.name, description=data.description, image_url=data.image_url,
            category=data.category, price=data.price, stock=data.stock, is_active=data.is_active)
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def update(self, db: Session, data: UpdateProductRequest, product_id: int) -> Product | None:
        # db.add() not needed — fetched objects are already tracked by SQLAlchemy session
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return None  # no product exists with this id — service raises ValueError
        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.image_url is not None:
            product.image_url = data.image_url
        if data.category is not None:
            product.category = data.category
        if data.price is not None:
            product.price = data.price
        if data.stock is not None:
            product.stock = data.stock
        if data.is_active is not None:
            product.is_active = data.is_active
        db.commit()
        db.refresh(product)
        return product

    def delete(self, db: Session, product_id: int) -> Product | None:
        # db.add() not needed — fetched objects are already tracked by SQLAlchemy session
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            return None  # no product exists with this id — service raises ValueError
        product.is_active = False
        db.commit()
        db.refresh(product)
        return product
