from datetime import datetime, timedelta, timezone
import secrets

from app.config.settings import settings
from app.core.util import Duration
from app.models.role import Role
from app.models.session import Session as SessionModel
from app.models.token import Token
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.token_repository import TokenRepository
from app.schemas.response.auth import LoginResult
from app.services.static.crypto_service import CryptoService
from app.services.static.email_service import EmailService
from app.services.static.jwt_service import JwtService
from app.services.static.password_service import PasswordService
from app.services.static.templating_service import TemplatingService
from app.services.user_service import UserService


class AuthService:
    VERIFICATION_TOKEN_LENGTH = 32
    PYSESSID_LENGTH: int = 32
    DEFAULT_AGE = timedelta(days=7)
    EXTENDED_AGE = timedelta(days=90)

    EMAIL_TOKEN_AGE = timedelta(days=1)
    PASSWORD_TOKEN_AGE = timedelta(hours=1)

    session_repo: SessionRepository
    token_repo: TokenRepository
    user_service: UserService

    email_service: type[EmailService]
    templating_service: type[TemplatingService]
    pw_service: type[PasswordService]
    crypto_service: type[CryptoService]
    jwt_service: type[JwtService]

    def __init__(
        self,
        session_repo: SessionRepository,
        token_repo: TokenRepository,
        user_service: UserService,
        email_service: type[EmailService],
        templating_service: type[TemplatingService],
        pw_service: type[PasswordService],
        crypto_service: type[CryptoService],
        jwt_service: type[JwtService],
    ):
        self.session_repo = session_repo
        self.token_repo = token_repo
        self.user_service = user_service
        self.email_service = email_service
        self.templating_service = templating_service
        self.pw_service = pw_service
        self.crypto_service = crypto_service
        self.jwt_service = jwt_service

    def authenticate(self, email: str, password: str, ip_address: str, user_agent: str, remember_me: bool) -> LoginResult | None:
        user = self.user_service.get_by_email(email)

        if user is None:
            print("No user with this email")
            return None

        if not self.pw_service.compare(user.password, password):
            print("Passwords do not match")
            return None

        pysessid = secrets.token_hex(self.PYSESSID_LENGTH)
        now = datetime.now(timezone.utc)
        exp = now + (self.EXTENDED_AGE if remember_me else self.DEFAULT_AGE)

        session = SessionModel(
            id=self.crypto_service.sha256hash(pysessid),
            uid=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            issued_at=now,
            expires_at=exp,
        )

        self.session_repo.save(session)

        # Load full user with role info so create_token can access permissions
        user_with_role = self.user_service.load_by_id(user.id)
        jwt = self.create_token(user_with_role)

        return LoginResult(
            pysessid=pysessid,
            access_token=jwt,
            expires_in=settings.jwt_expiry_minutes * 60,
        )

    def register(self, name: str, email: str, password: str, ip_address: str = "", user_agent: str = "") -> LoginResult | None:
        """Register a new user and return login result (auto-login).

        Returns ``None`` when the email is already taken.
        """
        # Check for duplicate email
        existing = self.user_service.get_by_email(email)
        if existing is not None:
            return None

        # Find or create default user role
        role_repo = self.user_service.role_repo
        default_role = role_repo.get_by("name", "user")
        if default_role is None:
            default_role = role_repo.save(Role(name="user", permissions=[], can_login=True))

        # Split name into first/last
        parts = name.strip().split(" ", 1)
        first_name = parts[0] or "Unknown"
        last_name = parts[1] if len(parts) > 1 else "User"

        now = datetime.now(timezone.utc)
        user = User(
            role_id=default_role.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=self.pw_service.hash(password),
            created_at=now,
        )
        saved_user = self.user_service.user_repo.save(user)

        # Create session
        pysessid = secrets.token_hex(self.PYSESSID_LENGTH)
        exp = now + self.DEFAULT_AGE

        session = SessionModel(
            id=self.crypto_service.sha256hash(pysessid),
            uid=saved_user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            issued_at=now,
            expires_at=exp,
        )
        self.session_repo.save(session)

        # Generate JWT
        user_with_role = self.user_service.load_by_id(saved_user.id)
        jwt = self.create_token(user_with_role)

        return LoginResult(
            pysessid=pysessid,
            access_token=jwt,
            expires_in=settings.jwt_expiry_minutes * 60,
        )

    def create_token(self, user) -> str:
        """Return a signed JWT string for *user*."""
        permissions: list[str] = []
        if hasattr(user, "permissions") and isinstance(user.permissions, list):
            permissions = user.permissions
        elif hasattr(user, "role") and hasattr(user.role, "permissions"):
            permissions = user.role.permissions

        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "permissions": permissions,
            "iat": now,
            "exp": now + timedelta(minutes=settings.jwt_expiry_minutes),
        }
        return self.jwt_service.encode(payload)

    def refresh(self, pysessid: str, user_agent: str, ip_address: str) -> str | None:
        """Validate a session and return a fresh JWT, or ``None`` on failure."""
        sessid_hash = self.crypto_service.sha256hash(pysessid)
        session = self.session_repo.get_by_id(sessid_hash)

        if session is None:
            return None

        now = datetime.now(timezone.utc)
        expires_at = session.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now:
            return None

        if session.revoked_at is not None:
            return None

        if session.user_agent != user_agent or session.ip_address != ip_address:
            self.session_repo.delete(session)
            return None

        user = self.user_service.load_by_id(session.uid)
        if user is None:
            return None

        return self.create_token(user)

    def revoke(self, pysessid: str) -> bool:
        """Revoke a session by its raw pysessid. Returns ``True`` if found."""
        sessid_hash = self.crypto_service.sha256hash(pysessid)
        session = self.session_repo.get_by_id(sessid_hash)

        if session is None:
            return False

        session.revoked_at = datetime.now(timezone.utc)
        self.session_repo.save(session)
        return True

    def create_email_verification(self, user: User):
        token = secrets.token_urlsafe(self.VERIFICATION_TOKEN_LENGTH)

        now = datetime.now(timezone.utc)

        self.token_repo.save(Token(
            token_hash=self.crypto_service.sha256hash(token),
            uid=user.id,
            issued_at=now,
            expires_at=now + self.PASSWORD_TOKEN_AGE
        ))

        url = f"{settings.frontend_url}/auth/password/verify?token={token}"

        html = self.templating_service.render('reset-password.html.j2').using({
            'first_name': user.first_name,
            'url': url,
            'expires_in': Duration.readable(self.PASSWORD_TOKEN_AGE)
        })

        self.email_service.send_html(user.email, 'Verify your email address', html)

    def verify_token(self, token: str, consume: bool = False) -> Token | None:
        token_hash = self.crypto_service.sha256hash(token)

        saved_token = self.token_repo.get_by('token_hash', token_hash)

        if not saved_token:
            return None

        now = datetime.now(timezone.utc)

        if saved_token.used_at is not None or saved_token.expires_at <= now:
            return None

        if consume:
            saved_token.used_at = now
            self.token_repo.save(saved_token)

        return saved_token

    def update_password(self, uid: int, password: str) -> None:
        password_hash = self.pw_service.hash(password)

        user = self.user_service.get_by_id(uid)

        if not user:
            return

        user.password = password_hash
        self.user_service.update(user)

    def get_session(self, pysessid: str) -> SessionModel | None:
        """Return the session for a raw pysessid (hashes before lookup)."""
        sessid_hash = self.crypto_service.sha256hash(pysessid)
        return self.session_repo.get_by_id(sessid_hash)
