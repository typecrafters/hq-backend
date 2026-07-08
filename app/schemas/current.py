from pydantic import BaseModel
from app.schemas.response.session import Session
from app.schemas.response.user_with_role import UserWithRole

class Current(BaseModel):
    session: Session
    user: UserWithRole