from datetime import datetime
from typing import Self
from pydantic import BaseModel
from app.schemas.internal.current import Current

class PublicRole(BaseModel):
    name: str
    permissions: list[str]

class Me(BaseModel):
    id: int
    first_name: str
    last_name: str
    title: str | None
    email: str
    profile_picture_url: str | None
    role: PublicRole
    session_id: str
    session_expires_at: datetime

    @classmethod
    def from_current(cls, current: Current) -> Self:
        return cls(
            id=current.user.id,
            first_name=current.user.first_name,
            last_name=current.user.last_name,
            title=current.user.title,
            email=current.user.email,
            profile_picture_url=current.user.profile_picture_url,
            role = PublicRole(
                name=current.user.role.name,
                permissions=current.user.role.permissions
            ),
            session_id=current.session.id,
            session_expires_at=current.session.expires_at
        )