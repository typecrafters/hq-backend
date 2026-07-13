"""Tests for AuthService JWT changes (Task 2.1).

Strict TDD: tests written BEFORE implementation code.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt as pyjwt
import pytest

from app.config.settings import settings
from app.schemas.response.auth import LoginResult
from app.schemas.response.role import RoleResponse
from app.schemas.response.user_with_role import UserWithRole
from app.services.auth_service import AuthService
from app.services.static.crypto_service import CryptoService
from app.services.static.jwt_service import JwtService
from app.services.static.password_service import PasswordService

# ── helpers ──────────────────────────────────────────────────────────────


def make_auth_service(
    session_repo: MagicMock | None = None,
    user_service: MagicMock | None = None,
    pw_service: type[PasswordService] | MagicMock | None = None,
    crypto_service: type[CryptoService] | None = None,
    jwt_service: type[JwtService] | None = None,
) -> AuthService:
    """Factory to build AuthService with convenient test defaults.

    ``pw_service`` defaults to a MagicMock so tests that don't exercise
    credential verification (create_token, refresh, revoke, get_session)
    don't incur the real Argon2 memory cost.
    """
    return AuthService(
        session_repo=session_repo or MagicMock(),
        user_service=user_service or MagicMock(),
        pw_service=pw_service or MagicMock(),
        crypto_service=crypto_service or CryptoService,
        jwt_service=jwt_service or JwtService,
    )


def make_user(**overrides) -> MagicMock:
    """Create a mock User (SQLAlchemy ORM model) with sensible defaults."""
    user = MagicMock()
    user.id = overrides.get("id", 1)
    user.email = overrides.get("email", "test@example.com")
    user.password = overrides.get("password", "fake-argon2-hash-for-testing")
    user.role_id = overrides.get("role_id", 1)
    return user


def make_user_with_role(**overrides) -> UserWithRole:
    """Create a UserWithRole schema instance with sensible defaults."""
    return UserWithRole(
        id=overrides.get("id", 1),
        role=overrides.get(
            "role",
            RoleResponse(id=1, name="test", permissions=["read", "write"], can_login=True),
        ),
        first_name=overrides.get("first_name", "Test"),
        last_name=overrides.get("last_name", "User"),
        title=overrides.get("title", ""),
        email=overrides.get("email", "test@example.com"),
        password_set=overrides.get("password_set", True),
        profile_picture_url=overrides.get("profile_picture_url", ""),
        show_on_page=overrides.get("show_on_page", True),
        created_at=overrides.get("created_at", datetime.now(timezone.utc)),
    )


def make_session(**overrides) -> MagicMock:
    """Create a mock Session with sensible defaults."""
    session = MagicMock()
    now = datetime.now(timezone.utc)
    session.id = overrides.get("id", CryptoService.sha256hash("test-pysessid"))
    session.uid = overrides.get("uid", 1)
    session.ip_address = overrides.get("ip_address", "127.0.0.1")
    session.user_agent = overrides.get("user_agent", "test-agent")
    session.issued_at = overrides.get("issued_at", now)
    session.expires_at = overrides.get("expires_at", now + timedelta(days=7))
    session.revoked_at = overrides.get("revoked_at", None)
    session.data = overrides.get("data", {})
    return session


# ── authenticate ─────────────────────────────────────────────────────────


class TestAuthenticate:
    """AuthService.authenticate() should return LoginResult on success, None on failure."""

    def test_returns_login_result_with_valid_jwt_and_pysessid(self) -> None:
        """Happy path: valid credentials → LoginResult with JWT and pysessid."""
        user = make_user(id=42, email="admin@site.com")
        user_with_role = make_user_with_role(id=42, email="admin@site.com")
        session_repo = MagicMock()
        user_service = MagicMock()
        user_service.get_by_email.return_value = user
        user_service.load_by_id.return_value = user_with_role
        pw_service = MagicMock(spec=PasswordService)
        pw_service.compare.return_value = True

        svc = make_auth_service(
            session_repo=session_repo,
            user_service=user_service,
            pw_service=pw_service,
        )
        result = svc.authenticate("admin@site.com", "correct-password", remember_me=False)

        assert result is not None
        assert isinstance(result, LoginResult)
        # pysessid should be a 64-char hex string (32 bytes)
        assert len(result.pysessid) == 64
        # Verify it's a valid JWT with correct claims
        decoded = JwtService.decode(result.access_token)
        assert decoded["sub"] == "42"
        assert decoded["email"] == "admin@site.com"
        assert decoded["permissions"] == ["read", "write"]
        assert result.expires_in == settings.jwt_expiry_minutes * 60

    def test_returns_none_on_wrong_password(self) -> None:
        """Wrong password → None."""
        user = make_user()
        user_service = MagicMock()
        user_service.get_by_email.return_value = user
        pw_service = MagicMock(spec=PasswordService)
        pw_service.compare.return_value = False

        svc = make_auth_service(user_service=user_service, pw_service=pw_service)
        result = svc.authenticate("admin@site.com", "wrong-password", remember_me=False)
        assert result is None

    def test_returns_none_on_unknown_email(self) -> None:
        """Unknown email → None."""
        user_service = MagicMock()
        user_service.get_by_email.return_value = None

        svc = make_auth_service(user_service=user_service)
        result = svc.authenticate("unknown@site.com", "password", remember_me=False)
        assert result is None


# ── create_token ──────────────────────────────────────────────────────────


class TestCreateToken:
    """AuthService.create_token() should produce a valid signed JWT."""

    def test_produces_valid_jwt(self) -> None:
        """The JWT returned by create_token should decode with correct claims."""
        user = make_user_with_role(id=7, email="user@site.com")
        svc = make_auth_service()
        token = svc.create_token(user)

        decoded = JwtService.decode(token)
        assert decoded["sub"] == "7"
        assert decoded["email"] == "user@site.com"
        assert decoded["permissions"] == ["read", "write"]
        # Should have iat and exp claims
        assert "iat" in decoded
        assert "exp" in decoded
        # exp should be in the future
        assert decoded["exp"] > datetime.now(timezone.utc).timestamp()


# ── refresh ──────────────────────────────────────────────────────────────


class TestRefresh:
    """AuthService.refresh() should return a JWT on valid session, None otherwise."""

    def test_returns_new_jwt_with_valid_session(self) -> None:
        """Valid, unexpired, unrevoked session → new JWT."""
        pysessid = "valid-pysessid-hex-string"
        hashed = CryptoService.sha256hash(pysessid)
        session = make_session(id=hashed, uid=42, ip_address="127.0.0.1", user_agent="test-agent")
        user = make_user_with_role(id=42, email="user@site.com")

        session_repo = MagicMock()
        session_repo.get_by_id.return_value = session
        user_service = MagicMock()
        user_service.load_by_id.return_value = user

        svc = make_auth_service(session_repo=session_repo, user_service=user_service)
        token = svc.refresh(pysessid, "test-agent", "127.0.0.1")

        assert token is not None
        decoded = JwtService.decode(token)
        assert decoded["sub"] == "42"
        assert decoded["email"] == "user@site.com"

    def test_returns_none_with_expired_session(self) -> None:
        """Expired session → None."""
        pysessid = "expired-session-hex"
        hashed = CryptoService.sha256hash(pysessid)
        session = make_session(
            id=hashed,
            uid=42,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = session

        svc = make_auth_service(session_repo=session_repo)
        token = svc.refresh(pysessid, "agent", "127.0.0.1")
        assert token is None

    def test_returns_none_with_revoked_session(self) -> None:
        """Revoked session → None."""
        pysessid = "revoked-session-hex"
        hashed = CryptoService.sha256hash(pysessid)
        session = make_session(
            id=hashed,
            uid=42,
            revoked_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        )
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = session

        svc = make_auth_service(session_repo=session_repo)
        token = svc.refresh(pysessid, "agent", "127.0.0.1")
        assert token is None

    def test_returns_none_with_wrong_user_agent(self) -> None:
        """Wrong user_agent → None, and session is deleted."""
        pysessid = "wrong-ua-hex"
        hashed = CryptoService.sha256hash(pysessid)
        session = make_session(id=hashed, uid=42, user_agent="real-agent", ip_address="127.0.0.1")
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = session

        svc = make_auth_service(session_repo=session_repo)
        token = svc.refresh(pysessid, "wrong-agent", "127.0.0.1")
        assert token is None
        session_repo.delete.assert_called_once_with(session)

    def test_returns_none_on_session_not_found(self) -> None:
        """Unknown pysessid → None."""
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = None

        svc = make_auth_service(session_repo=session_repo)
        token = svc.refresh("unknown", "agent", "127.0.0.1")
        assert token is None


# ── revoke ────────────────────────────────────────────────────────────────


class TestRevoke:
    """AuthService.revoke() should set revoked_at and return True, or False if not found."""

    def test_sets_revoked_at_and_returns_true(self) -> None:
        """Existing session → revoked_at set, save called, returns True."""
        pysessid = "valid-session-hex"
        hashed = CryptoService.sha256hash(pysessid)
        session = make_session(id=hashed, uid=42)
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = session

        svc = make_auth_service(session_repo=session_repo)
        result = svc.revoke(pysessid)

        assert result is True
        assert session.revoked_at is not None
        assert isinstance(session.revoked_at, datetime)
        session_repo.save.assert_called_once_with(session)

    def test_returns_false_for_unknown_pysessid(self) -> None:
        """Unknown pysessid → False, no save."""
        session_repo = MagicMock()
        session_repo.get_by_id.return_value = None

        svc = make_auth_service(session_repo=session_repo)
        result = svc.revoke("unknown")
        assert result is False
        session_repo.save.assert_not_called()


# ── get_session fix ──────────────────────────────────────────────────────


class TestGetSession:
    """AuthService.get_session() should hash pysessid before lookup (bug fix)."""

    def test_hashes_before_lookup(self) -> None:
        """get_session should SHA-256 hash pysessid before calling get_by_id."""
        pysessid = "raw-session-id"
        hashed = CryptoService.sha256hash(pysessid)

        session_repo = MagicMock()
        expected_session = MagicMock()
        session_repo.get_by_id.return_value = expected_session

        svc = make_auth_service(session_repo=session_repo)
        result = svc.get_session(pysessid)

        assert result is expected_session
        session_repo.get_by_id.assert_called_once_with(hashed)
