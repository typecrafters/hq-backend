from pydantic import BaseModel

class CreateMessage(BaseModel):
    full_name: str
    email: str
    message: str