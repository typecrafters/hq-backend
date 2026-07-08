from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import settings
from app.db.base import Base

engine = create_engine(
    settings.database_url(),
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 10,
        "application_name": "hq-backend",
        "options": "-c timezone=UTC",
    },
)

def create_db():
    Base.metadata.create_all(engine)