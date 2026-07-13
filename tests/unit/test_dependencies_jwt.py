"""Unit tests for JWT Bearer token dependency (Task 3.2).

Tests the ``get_current_user`` function directly (not via TestClient) since
it's a deterministic function: same ``authorization`` string → same result.
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.config.settings import settings
from app.dependencies import get_current_user
from app.schemas.current_user import CurrentUser
from app.services.static.jwt_service import JwtService


class TestGetCurrentUser:
    """get_current_user() returns CurrentUser from valid Bearer token, 401 otherwise."""

    def test_returns_current_user_with_valid_bearer_token(self) -> None:
        """Valid Bearer token → CurrentUser with correct id, email, permissions."""
        payload = {
            "sub": "42",
            "email": "admin@site.com",
            "permissions": ["read", "write"],
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        token = JwtService.encode(payload)

        result = get_current_user(authorization=f"Bearer {token}")

        assert isinstance(result, CurrentUser)
        assert result.id == 42  # converted from str "42" to int
        assert result.email == "admin@site.com"
        assert result.permissions == ["read", "write"]

    def test_raises_401_without_authorization_header(self) -> None:
        """No Authorization header → 401."""
        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization=None)
        assert exc.value.status_code == 401

    def test_raises_401_with_wrong_scheme(self) -> None:
        """Authorization with 'Basic' scheme instead of 'Bearer' → 401."""
        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization="Basic some-token")
        assert exc.value.status_code == 401

    def test_raises_401_with_expired_token(self) -> None:
        """Expired JWT → 401."""
        payload = {
            "sub": "1",
            "email": "user@site.com",
            "permissions": [],
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = JwtService.encode(payload)

        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization=f"Bearer {token}")
        assert exc.value.status_code == 401

    def test_raises_401_with_tampered_token(self) -> None:
        """Token with invalid signature → 401."""
        payload = {
            "sub": "1",
            "email": "user@site.com",
            "permissions": [],
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        token = JwtService.encode(payload)
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.invalidsignature"

        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization=f"Bearer {tampered}")
        assert exc.value.status_code == 401

    def test_raises_401_with_malformed_header_no_space(self) -> None:
        """Authorization header without space separator → 401."""
        with pytest.raises(HTTPException) as exc:
            get_current_user(authorization="BearerTokenWithNoSpace")
        assert exc.value.status_code == 401
