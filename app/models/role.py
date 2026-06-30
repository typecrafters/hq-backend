from sqlalchemy import ARRAY as Array, BigInteger, Boolean, Identity, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String)  
    permissions: Mapped[list[str]] = mapped_column(Array(String))
    can_login: Mapped[bool] = mapped_column(Boolean, default=False)
