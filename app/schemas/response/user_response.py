from typing import Self
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.user import User


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    first_name: str
    last_name: str
    title: str | None
    email: str
    password_set: bool
    profile_picture_url: str | None
    show_on_page: bool
    created_at: datetime

    @classmethod
    def from_model(cls, model: User) -> Self:
        return cls(
            id=model.id,
            role_id=model.role_id,
            first_name=model.first_name,
            last_name=model.last_name,
            title=model.title,
            email=model.email,
            password_set=model.password is not None and not model.password.strip() == '',
            profile_picture_url=model.profile_picture_url,
            show_on_page=model.show_on_page,
            created_at=model.created_at
        )