from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel
from app.repositories.repository import Repository

class SessionRepository(Repository[SessionModel, str]):
    def __init__(self, db: Session):
        super().__init__(db, SessionModel)
