from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.token import Token
from app.repositories.repository import Repository

class TokenRepository(Repository[Token, int]):
    def __init__(self, db: Session):
        super().__init__(db, Token)
    def delete_all_expired(self) -> None:
        self.db.execute(delete(Token).where(Token.expires_at <= datetime.now(timezone.utc)))
