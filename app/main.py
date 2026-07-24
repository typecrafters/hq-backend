import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path
from alembic.config import Config
from alembic import command
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api
from app.config.settings import settings
from app.error.handlers import log_exceptions

def run_migrations() -> None:
    alembic_ini = Path(__file__).resolve().parent.parent / 'alembic.ini'
    alembic_cfg = Config(str(alembic_ini))
    command.upgrade(alembic_cfg, 'head')


@asynccontextmanager
def lifespan(_: FastAPI):
    run_migrations()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods_list(),
    allow_headers=settings.cors_headers_list(),
)

app.add_exception_handler(Exception, log_exceptions)
app.include_router(api.router)


if __name__ == '__main__':
    run_migrations()
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
