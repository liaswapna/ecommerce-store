from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.product import CreateProductRequest, UpdateProductRequest, ProductResponse
from app.services.product import ProductService
from app.dependencies import require_admin
from app.models.user import User
from app.exceptions import NotFoundError, DatabaseError

router = APIRouter(prefix="/products", tags=["Product"])
admin_router = APIRouter(prefix="/admin/products", tags=["Admin Products"])
service = ProductService()


@router.get("/", response_model=list[ProductResponse])
def get_all(page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    return service.get_all(db, page, page_size, True)


@router.get("/category/{category}", response_model=list[ProductResponse])
def get_by_category(category: str, page: int = 1, page_size: int = 10, db: Session = Depends(get_db)):
    return service.get_by_category(db, category, page, page_size, True)


@router.get("/{product_id}", response_model=ProductResponse)
def get_by_id(product_id: int, db: Session = Depends(get_db)):
    try:
        return service.get_by_id(db, product_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@admin_router.get("/", response_model=list[ProductResponse])
def admin_get_all(page: int = 1, page_size: int = 10, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return service.get_all(db, page, page_size, False)


@admin_router.get("/category/{category}", response_model=list[ProductResponse])
def admin_get_by_category(category: str, page: int = 1, page_size: int = 10, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return service.get_by_category(db, category, page, page_size, False)


@admin_router.get("/{product_id}", response_model=ProductResponse)
def admin_get_by_id(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try:
        return service.get_by_id(db, product_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@admin_router.post("/", response_model=ProductResponse)
def create(data: CreateProductRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try:
        return service.create(db, data)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.put("/{product_id}", response_model=ProductResponse)
def update(product_id: int, data: UpdateProductRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try:
        return service.update(db, data, product_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@admin_router.delete("/{product_id}", response_model=ProductResponse)
def delete(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try:
        return service.delete(db, product_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
