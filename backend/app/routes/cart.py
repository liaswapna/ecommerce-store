from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.cart import AddCartRequest, UpdateCartRequest, CartItemResponse, CartItemDetailResponse
from app.services.cart import CartService
from app.dependencies import get_current_user
from app.models.user import User
from app.exceptions import NotFoundError, DatabaseError, OutOfStockError


router = APIRouter(prefix="/cart", tags=["Cart"])
service = CartService()


@router.get("/", response_model=list[CartItemDetailResponse])
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_cart_details(db, current_user.id)


@router.post("/", response_model=CartItemResponse)
def add_to_cart(request: AddCartRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.add_to_cart(db, current_user.id, request)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OutOfStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/", response_model=CartItemResponse)
def update_cart(request: UpdateCartRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.update_cart(db, current_user.id, request)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OutOfStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


# clear_cart must be registered before delete_from_cart — FastAPI matches routes top to bottom
# and /{product_id} would swallow /clear as a string param if ordered first
@router.delete("/clear")
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.clear_cart(db, current_user.id)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}", response_model=CartItemResponse)
def delete_from_cart(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.delete_from_cart(db, current_user.id, product_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
