from datetime import datetime, timedelta
from sqlalchemy import select
from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.repositories.repository import Repository


class PasswordResetTokenRepository(Repository):

    def get_valid_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > datetime.now(),
        ).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, user: User, token_hash: str, max_age: timedelta) -> None:
        now = datetime.now()

        token = PasswordResetToken(
            token_hash=token_hash,
            uid=user.id,
            issued_at=now,
            expires_at=now + max_age,
        )

        self.db.add(token)

    def mark_used(self, token: PasswordResetToken) -> None:
        token.used_at = datetime.now()
