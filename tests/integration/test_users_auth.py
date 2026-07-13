"""Integration tests for protected user routes (Task 3.3).

Uses FastAPI TestClient with dependency overrides on ``get_user_service``.
Authentication is exercised with real JWT tokens via the ``Authorization``
header so the full ``get_current_user`` dependency runs end-to-end.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_user_service
from app.main import app
from app.services.static.jwt_service import JwtService


@pytest.fixture
def mock_user_service():
    svc = MagicMock()
    svc.list.return_value = [
        {"id": 1, "email": "admin@site.com", "first_name": "Admin"},
    ]
    svc.create.return_value = {
        "id": 2,
        "email": "new@site.com",
        "first_name": "New",
    }
    yield svc


@pytest.fixture
def client(mock_user_service):
    """TestClient with user_service dependency overridden."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── helpers ──────────────────────────────────────────────────────────────


def _valid_token(**overrides) -> str:
    """Create a signed JWT with sensible defaults for tests."""
    payload = {
        "sub": "1",
        "email": overrides.get("email", "admin@site.com"),
        "permissions": overrides.get("permissions", []),
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=overrides.get("expiry_minutes", 15)),
    }
    return JwtService.encode(payload)


# ── GET /users ───────────────────────────────────────────────────────────


class TestListUsers:
    """GET /users should list users when authenticated, 401 otherwise."""

    def test_returns_200_with_valid_bearer_token(
        self, client, mock_user_service
    ) -> None:
        """Valid Bearer token → 200, user_service.list called."""
        token = _valid_token()
        response = client.get(
            "/v1/users?page=1&limit=10",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        mock_user_service.list.assert_called_once_with(1, 10)

    def test_returns_401_without_bearer_token(self, client) -> None:
        """No Authorization header → 401."""
        response = client.get("/v1/users?page=1&limit=10")
        assert response.status_code == 401

    def test_returns_401_with_expired_token(self, client) -> None:
        """Expired JWT token → 401."""
        token = _valid_token(expiry_minutes=-30)  # expired 30 min ago
        response = client.get(
            "/v1/users?page=1&limit=10",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    def test_returns_401_with_tampered_token(self, client) -> None:
        """Token with invalid signature → 401."""
        token = _valid_token()
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.bad"
        response = client.get(
            "/v1/users?page=1&limit=10",
            headers={"Authorization": f"Bearer {tampered}"},
        )
        assert response.status_code == 401


# ── POST /users ──────────────────────────────────────────────────────────


class TestSaveUser:
    """POST /users should create a user when authenticated, 401 otherwise."""

    def test_returns_200_with_valid_bearer_token(
        self, client, mock_user_service
    ) -> None:
        """Valid Bearer token → 200, user_service.create called."""
        token = _valid_token()
        response = client.post(
            "/v1/users",
            json={
                "email": "new@site.com",
                "firstName": "New",
                "lastName": "User",
                "password": "secret",
                "title": "Dev",
                "permissions": [],
                "canAccessPanel": True,
                "createRole": False,
                "showOnPage": True,
                "profilePictureUrl": "",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        mock_user_service.create.assert_called_once()

    def test_returns_401_without_bearer_token(self, client) -> None:
        """No Authorization header → 401."""
        response = client.post(
            "/v1/users",
            json={
                "email": "hacker@site.com",
                "firstName": "Hack",
                "lastName": "Er",
                "password": "evil",
                "title": "Hacker",
                "permissions": [],
                "canAccessPanel": True,
                "createRole": False,
                "showOnPage": True,
                "profilePictureUrl": "",
            },
        )
        assert response.status_code == 401

    def test_returns_401_with_expired_token(self, client) -> None:
        """Expired JWT token → 401."""
        token = _valid_token(expiry_minutes=-30)
        response = client.post(
            "/v1/users",
            json={
                "email": "hacker@site.com",
                "firstName": "Hack",
                "lastName": "Er",
                "password": "evil",
                "title": "Hacker",
                "permissions": [],
                "canAccessPanel": True,
                "createRole": False,
                "showOnPage": True,
                "profilePictureUrl": "",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    def test_returns_401_with_tampered_token(self, client) -> None:
        """Token with invalid signature → 401."""
        token = _valid_token()
        parts = token.split(".")
        tampered = f"{parts[0]}.{parts[1]}.bad"
        response = client.post(
            "/v1/users",
            json={
                "email": "hacker@site.com",
                "firstName": "Hack",
                "lastName": "Er",
                "password": "evil",
                "title": "Hacker",
                "permissions": [],
                "canAccessPanel": True,
                "createRole": False,
                "showOnPage": True,
                "profilePictureUrl": "",
            },
            headers={"Authorization": f"Bearer {tampered}"},
        )
        assert response.status_code == 401
