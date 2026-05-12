from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

service = AuthService()
repository = UserRepository()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        user_id = service.decode_token(token)
        user = repository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        return user

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
