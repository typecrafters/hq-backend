from sqlalchemy import create_engine
from app.config.settings import settings
from app.db.base import Base

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

def create_db():
    from app.models.message import Message
    from app.models.post import Post
    from app.models.project import Project
    from app.models.role import Role
    from app.models.session import Session
    from app.models.token import Token
    from app.models.user import User
    Base.metadata.create_all(engine)