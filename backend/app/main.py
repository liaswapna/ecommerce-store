from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, database
from app.models import user
from app.routes import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=database.engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
