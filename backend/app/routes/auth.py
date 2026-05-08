from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = service.register(
            db, request.name, request.email, request.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        token = service.login(db, request.email, request.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
