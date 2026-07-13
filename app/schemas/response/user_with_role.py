from datetime import datetime
from pydantic import BaseModel

from app.schemas.response.role import RoleResponse

class UserWithRole(BaseModel):
    id: int
    role: RoleResponse
    first_name: str
    last_name: str
    title: str | None
    email: str
    password_set: bool
    profile_picture_url: str | None
    show_on_page: bool
    created_at: datetime
