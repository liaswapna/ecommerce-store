from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


class Database:
    """Manages database connection and session lifecycle."""

    def __init__(self, url: str):
        self.engine = create_engine(url)
        self.session = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self):
        """Yields a database session per request ans ensures it is closed after use."""
        db = self.session()
        try:
            yield db
        finally:
            db.close()


database = Database(settings.database_url)
get_db = database.get_session
