from pydantic import BaseModel

class ReplyToMessage(BaseModel):
    reply: str