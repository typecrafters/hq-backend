from pydantic import BaseModel
from app.models.session import Session
from app.models.user import User

class Current(BaseModel):
    session: Session
    user: User