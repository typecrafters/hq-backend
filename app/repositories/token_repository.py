from sqlalchemy.orm import Session

from app.models.token import Token
from app.repositories.repository import Repository

class TokenRepository(Repository[Token, int]):
    def __init__(self, db: Session):
        super().__init__(db, Token)
