from datetime import datetime
from pydantic import BaseModel

class ProtectedUser(BaseModel):
    id: int
    role_id: int
    first_name: str
    last_name: str
    title: str
    email: str
    password_set: bool
    profile_picture_url: str
    show_on_page: bool
    created_at: datetime