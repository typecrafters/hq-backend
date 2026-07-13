"""Integration tests for auth routes (Task 3.1) — login, refresh, logout.

Uses FastAPI TestClient with dependency overrides on get_auth_service.
"""

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.dependencies import get_auth_service
from app.main import app
from app.schemas.response.auth import LoginResult, TokenResponse


@pytest.fixture
def mock_auth_service():
    """Create a mock AuthService for dependency override.

    Sets up both instance-level attributes (used by the route code)
    and method return values that each test can customize.
    """
    svc = MagicMock()
    svc.DEFAULT_AGE = timedelta(days=7)
    svc.EXTENDED_AGE = timedelta(days=90)
    yield svc


@pytest.fixture
def client(mock_auth_service):
    """TestClient with the auth service dependency overridden."""
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── POST /api/v1/auth/login ──────────────────────────────────────────────


class TestLogin:
    """POST /auth/login should return token on success, 401 on failure."""

    def test_returns_200_with_token_and_set_cookie(self, client, mock_auth_service):
        """Valid credentials → 200 with TokenResponse body + Set-Cookie."""
        expected_expires_in = settings.jwt_expiry_minutes * 60
        mock_auth_service.authenticate.return_value = LoginResult(
            pysessid="test-pysessid-hex123",
            access_token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.test",
            expires_in=expected_expires_in,
        )

        response = client.post(
            "/v1/auth/login",
            json={"email": "admin@site.com", "password": "correct", "rememberMe": False},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["accessToken"] == "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.test"
        assert body["tokenType"] == "bearer"
        assert body["expiresIn"] == expected_expires_in
        # Must include a Set-Cookie header for pysessid
        set_cookie = response.headers.get("set-cookie", "")
        assert "pysessid" in set_cookie

    def test_returns_401_with_wrong_credentials(self, client, mock_auth_service):
        """Invalid credentials → 401."""
        mock_auth_service.authenticate.return_value = None

        response = client.post(
            "/v1/auth/login",
            json={"email": "admin@site.com", "password": "wrong", "rememberMe": False},
        )

        assert response.status_code == 401


# ── POST /api/v1/auth/refresh ────────────────────────────────────────────


class TestRefresh:
    """POST /auth/refresh should return a new token or 401."""

    def test_returns_200_with_new_token_given_valid_cookie(self, client, mock_auth_service):
        """Valid pysessid cookie → 200 with new TokenResponse body."""
        expected = TokenResponse(access_token="new-jwt-token", expires_in=900)
        # Return raw string from refresh (route wraps it in TokenResponse)
        mock_auth_service.refresh.return_value = "new-jwt-token"

        response = client.post(
            "/v1/auth/refresh",
            cookies={"pysessid": "valid-session-hex"},
            headers={"user-agent": "test-agent"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["accessToken"] == "new-jwt-token"
        assert body["tokenType"] == "bearer"
        assert body["expiresIn"] == 900

    def test_returns_401_without_cookie(self, client, mock_auth_service):
        """No pysessid cookie → 401."""
        mock_auth_service.refresh.return_value = None

        response = client.post("/v1/auth/refresh")
        assert response.status_code == 401

    def test_returns_401_with_expired_session(self, client, mock_auth_service):
        """Expired session (mock returns None) → 401."""
        mock_auth_service.refresh.return_value = None

        response = client.post(
            "/v1/auth/refresh",
            cookies={"pysessid": "expired-session-hex"},
        )
        assert response.status_code == 401


# ── POST /api/v1/auth/logout ──────────────────────────────────────────────


class TestLogout:
    """POST /auth/logout should clear cookie and return 204."""

    def test_returns_204_and_clears_cookie(self, client, mock_auth_service):
        """Valid session → 204, cookie cleared, revoke called."""
        mock_auth_service.revoke.return_value = True

        response = client.post(
            "/v1/auth/logout",
            cookies={"pysessid": "valid-session-hex"},
        )

        assert response.status_code == 204
        mock_auth_service.revoke.assert_called_once_with("valid-session-hex")
        # Set-Cookie should clear the pysessid cookie
        set_cookie = response.headers.get("set-cookie", "")
        assert "pysessid" in set_cookie
        # Typically max-age=0 or expires in the past means "delete this cookie"
        assert "max-age=0" in set_cookie or "Max-Age=0" in set_cookie

    def test_graceful_without_cookie(self, client, mock_auth_service):
        """No cookie → still 204, no error, revoke not called."""
        mock_auth_service.revoke.return_value = False

        response = client.post("/v1/auth/logout")
        assert response.status_code == 204
        # Without a cookie the route should just clear and return, not revoke
        mock_auth_service.revoke.assert_not_called()
