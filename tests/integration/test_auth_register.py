"""Integration tests for the register endpoint (POST /auth/register).

Uses FastAPI TestClient with dependency overrides on get_auth_service.
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.dependencies import get_auth_service
from app.main import app
from app.schemas.response.auth import LoginResult
from datetime import timedelta


@pytest.fixture
def mock_auth_service():
    """Create a mock AuthService for dependency override."""
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


class TestRegister:
    """POST /auth/register should create user and return token, or 409 on duplicate."""

    def test_returns_201_with_token_and_set_cookie(self, client, mock_auth_service):
        """New email → 201 with TokenResponse body + Set-Cookie."""
        expected_expires_in = settings.jwt_expiry_minutes * 60
        mock_auth_service.register.return_value = LoginResult(
            pysessid="new-session-hex123",
            access_token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyIn0.newtoken",
            expires_in=expected_expires_in,
        )

        response = client.post(
            "/v1/auth/register",
            json={"name": "Jane Doe", "email": "jane@example.com", "password": "secure456"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["accessToken"] == "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIyIn0.newtoken"
        assert body["tokenType"] == "bearer"
        assert body["expiresIn"] == expected_expires_in
        # Set-Cookie for pysessid
        set_cookie = response.headers.get("set-cookie", "")
        assert "pysessid" in set_cookie

    def test_returns_409_with_duplicate_email(self, client, mock_auth_service):
        """Existing email → 409."""
        mock_auth_service.register.return_value = None

        response = client.post(
            "/v1/auth/register",
            json={"name": "Jane Doe", "email": "existing@example.com", "password": "secure456"},
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already registered."
