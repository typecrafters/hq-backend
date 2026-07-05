from sqlalchemy.orm import Session

from app.models.message import Message
from app.repositories.repository import Repository

class MessageRepository(Repository[Message, int]):
    def __init__(self, db: Session):
        super().__init__(db, Message)
