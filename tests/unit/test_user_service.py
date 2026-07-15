"""Unit tests for UserService.

Uses mocked repositories so no real database is needed.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.models.role import Role
from app.models.user import User
from app.schemas.request.create_user import CreateUser
from app.schemas.response.role import RoleResponse
from app.services.user_service import UserService


@pytest.fixture
def mock_user_repo():
    return MagicMock()


@pytest.fixture
def mock_role_repo():
    return MagicMock()


@pytest.fixture
def mock_token_repo():
    return MagicMock()


@pytest.fixture
def mock_file_service():
    return MagicMock()


@pytest.fixture
def mock_email_service():
    return MagicMock()


@pytest.fixture
def mock_templating_service():
    return MagicMock()


@pytest.fixture
def mock_crypto_service():
    return MagicMock()


@pytest.fixture
def user_service(
    mock_user_repo,
    mock_role_repo,
    mock_token_repo,
    mock_file_service,
    mock_email_service,
    mock_templating_service,
    mock_crypto_service,
):
    return UserService(
        user_repo=mock_user_repo,
        role_repo=mock_role_repo,
        token_repo=mock_token_repo,
        file_service=mock_file_service,
        email_service=mock_email_service,
        templating_service=mock_templating_service,
        crypto_service=mock_crypto_service,
    )


class TestUserService:
    """Covers UserService: get_by_id, get_by_email, list, create, load_by_id."""

    # ── get_by_id ──────────────────────────────────────────────────────────

    def test_get_by_id_returns_user(self, user_service, mock_user_repo):
        expected = User(id=1, first_name="Test", last_name="User", email="t@t.com")
        mock_user_repo.get_by_id.return_value = expected

        result = user_service.get_by_id(1)
        assert result == expected
        mock_user_repo.get_by_id.assert_called_once_with(1)

    def test_get_by_id_returns_none_when_missing(self, user_service, mock_user_repo):
        mock_user_repo.get_by_id.return_value = None
        assert user_service.get_by_id(999) is None

    # ── get_by_email ───────────────────────────────────────────────────────

    def test_get_by_email_returns_user(self, user_service, mock_user_repo):
        expected = User(id=2, email="a@b.com")
        mock_user_repo.get_by_email.return_value = expected

        result = user_service.get_by_email("a@b.com")
        assert result == expected
        mock_user_repo.get_by_email.assert_called_once_with("a@b.com")

    def test_get_by_email_returns_none_when_missing(self, user_service, mock_user_repo):
        mock_user_repo.get_by_email.return_value = None
        assert user_service.get_by_email("missing@test.com") is None

    # ── list ───────────────────────────────────────────────────────────────

    def test_list_calls_get_all_with_defaults(self, user_service, mock_user_repo):
        mock_user_repo.get_all.return_value = []
        result = user_service.list(page=1, limit=20)
        mock_user_repo.get_all.assert_called_once_with(limit=20, offset=0)
        assert result == []

    def test_list_caps_limit_at_100(self, user_service, mock_user_repo):
        mock_user_repo.get_all.return_value = []
        user_service.list(page=1, limit=200)
        mock_user_repo.get_all.assert_called_once_with(limit=100, offset=0)

    def test_list_enforces_min_page(self, user_service, mock_user_repo):
        mock_user_repo.get_all.return_value = []
        user_service.list(page=0, limit=10)
        mock_user_repo.get_all.assert_called_once_with(limit=10, offset=0)

    def test_list_calculates_offset(self, user_service, mock_user_repo):
        mock_user_repo.get_all.return_value = []
        user_service.list(page=3, limit=10)
        mock_user_repo.get_all.assert_called_once_with(limit=10, offset=20)

    # ── create ─────────────────────────────────────────────────────────────

    def test_create_creates_role_and_user(self, user_service, mock_user_repo, mock_role_repo):
        data = CreateUser(
            first_name="John",
            last_name="Doe",
            title="Tester",
            email="john@test.com",
            password="secret",
            permissions=["read"],
            can_access_panel=True,
            create_role=False,
            show_on_page=True,
            profile_picture_url="",
        )
        mock_role_repo.save.return_value = Role(id=10, name="John_Doe_role", permissions=["read"], can_login=True)

        def _fake_user_save(user):
            user.id = 42
            return user

        mock_user_repo.save.side_effect = _fake_user_save

        result = user_service.create(data)

        assert result.id == 42
        assert result.first_name == "John"
        mock_role_repo.save.assert_called_once()
        mock_user_repo.save.assert_called_once()

    def test_create_with_extra_role(self, user_service, mock_user_repo, mock_role_repo):
        """When create_role=True, save a second permission-group role."""
        data = CreateUser(
            first_name="Jane",
            last_name="Doe",
            title="",
            email="jane@test.com",
            password="pwd",
            permissions=["manage"],
            can_access_panel=True,
            create_role=True,
            show_on_page=True,
            profile_picture_url="",
        )
        mock_role_repo.save.return_value = Role(id=20, name="Jane_Doe_role", permissions=["manage"], can_login=True)

        def _fake_user_save(user):
            user.id = 99
            return user

        mock_user_repo.save.side_effect = _fake_user_save

        result = user_service.create(data)
        assert result.id == 99
        # save was called twice — once for main role, once for pgroup role
        assert mock_role_repo.save.call_count == 2

    # ── load_by_id ─────────────────────────────────────────────────────────

    def test_load_by_id_returns_user_with_role(self, user_service, mock_user_repo, mock_role_repo):
        now = datetime.now(timezone.utc)
        user = User(
            id=1, role_id=5, first_name="John", last_name="Doe",
            title="Dev", email="john@test.com", show_on_page=True,
            created_at=now,
        )
        mock_user_repo.get_by_id.return_value = user
        role = Role(id=5, name="admin", permissions=["*"], can_login=True)
        mock_role_repo.get_by_id.return_value = role

        result = user_service.load_by_id(1)
        assert result is not None
        assert result.email == "john@test.com"
        assert result.role.name == "admin"
        assert result.role.permissions == ["*"]

    def test_load_by_id_returns_none_when_user_missing(self, user_service, mock_user_repo, mock_role_repo):
        mock_user_repo.get_by_id.return_value = None
        assert user_service.load_by_id(999) is None

    def test_load_by_id_returns_none_when_role_missing(self, user_service, mock_user_repo, mock_role_repo):
        user = User(id=1, role_id=999, first_name="X", last_name="Y", email="x@y.com")
        mock_user_repo.get_by_id.return_value = user
        mock_role_repo.get_by_id.return_value = None
        assert user_service.load_by_id(1) is None
