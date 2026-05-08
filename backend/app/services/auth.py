from datetime import datetime, timedelta, timezone
import jwt
from bcrypt import hashpw, checkpw, gensalt
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user import UserRepository
from app.config import settings


SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

repository = UserRepository()


class AuthService:
    def hash_password(self, password: str) -> str:
        return hashpw(password.encode(), gensalt()).decode()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return checkpw(plain.encode(), hashed.encode())

    def create_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + \
            timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def register(self, db: Session, name: str, email: str, password: str) -> User:
        existing = repository.get_by_email(db, email)
        if existing:
            raise ValueError("Email already registered")
        hashed = self.hash_password(password)
        return repository.create(db, name, email, hashed)

    def login(self, db: Session, email: str, password: str) -> str:
        user = repository.get_by_email(db, email)
        if not user or not self.verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")
        return self.create_token(user.id)
