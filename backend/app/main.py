from contextlib import asynccontextmanager
from fastapi import FastAPI
from alembic.config import Config
from alembic import command


@asynccontextmanager
async def lifespan(app: FastAPI):
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield


from app.routes import auth

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
