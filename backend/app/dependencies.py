from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService

# extracts the Bearer token from Authorization header on every request — returns 401 if no token present
security = HTTPBearer()

service = AuthService()
repository = UserRepository()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    token = credentials.credentials
    try:
        user_id = service.decode_token(token)
        user = repository.get_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")
        return user

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
