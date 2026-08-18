from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.order import OrderSummaryResponse, OrderDetailResponse
from app.services.order import OrderService
from app.dependencies import get_current_user
from app.models.user import User
from app.exceptions import NotFoundError, DatabaseError, OutOfStockError

router = APIRouter(prefix="/orders", tags=["order"])
service = OrderService()


@router.post("/", response_model=OrderDetailResponse)
def place_order(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.place_order(db, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OutOfStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[OrderSummaryResponse])
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return service.get_orders(db, current_user.id)


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order_by_id(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return service.get_order_by_id(db, order_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
