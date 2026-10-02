from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


class Database:
    """Manages database connection and session lifecycle."""

    def __init__(self, url: str):
        # pool_pre_ping: checks a saved connection is still alive (SELECT 1) before using it.
        # Neon free tier pauses the DB after 5 min idle, which kills saved connections -
        # without this, the first request after a pause would fail with a 500 error.
        self.engine = create_engine(url, pool_pre_ping=True)
        self.Session = sessionmaker(
            autocommit=False,
            autoflush=False,  # prevents SQLAlchemy from sending queries mid-transaction
            bind=self.engine
        )

    def get_session(self):
        """Yields a database session per request and ensures it is closed after use."""
        db = self.Session()
        try:
            yield db
        finally:
            db.close()


database = Database(settings.database_url)
get_db = database.get_session
