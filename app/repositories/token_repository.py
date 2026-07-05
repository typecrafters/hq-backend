from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.token import Token
from app.models.user import User
from app.repositories.repository import Repository


class TokenRepository(Repository):

    def get_valid_by_token_hash(self, token_hash: str) -> Token | None:
        stmt = select(Token).where(
            Token.token_hash == token_hash,
            Token.used_at.is_(None),
            Token.expires_at > datetime.now(),
        ).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user: User, token_hash: str, max_age: timedelta) -> None:
        now = datetime.now()

        token = Token(
            token_hash=token_hash,
            uid=user.id,
            issued_at=now,
            expires_at=now + max_age,
        )

        self.db.add(token)

    def mark_used(self, token: Token) -> None:
        token.used_at = datetime.now()
