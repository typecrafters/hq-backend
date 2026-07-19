from sqlalchemy import create_engine
from app.config.settings import settings

engine = create_engine(
    settings.db_url,
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