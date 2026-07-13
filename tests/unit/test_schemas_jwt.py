"""Tests for JWT-related Pydantic schemas (Task 1.3).

All schemas are pure data models — tests verify instantiation,
field access, and serialization/deserialization.
"""

import pytest
from pydantic import ValidationError

from app.schemas.current_user import CurrentUser
from app.schemas.response.auth import LoginResult, TokenResponse

# ── TokenResponse ────────────────────────────────────────────────────────


class TestTokenResponse:
    """TokenResponse model for JWT access token responses."""

    def test_instantiation_with_required_fields(self) -> None:
        """TokenResponse should accept access_token and expires_in."""
        tr = TokenResponse(access_token="eyJ.eyJ.sig", expires_in=900)
        assert tr.access_token == "eyJ.eyJ.sig"
        assert tr.expires_in == 900

    def test_token_type_defaults_to_bearer(self) -> None:
        """token_type should default to 'bearer'."""
        tr = TokenResponse(access_token="tok", expires_in=900)
        assert tr.token_type == "bearer"

    def test_serializes_to_dict(self) -> None:
        """Model must serialize to a dict with correct values."""
        tr = TokenResponse(access_token="abc.def.ghi", expires_in=600)
        d = tr.model_dump()
        assert d["access_token"] == "abc.def.ghi"
        assert d["token_type"] == "bearer"
        assert d["expires_in"] == 600

    def test_rejects_missing_required_fields(self) -> None:
        """Creating without access_token or expires_in should fail."""
        with pytest.raises(ValidationError):
            TokenResponse(access_token="tok")  # missing expires_in
        with pytest.raises(ValidationError):
            TokenResponse(expires_in=900)  # missing access_token


# ── LoginResult ──────────────────────────────────────────────────────────


class TestLoginResult:
    """LoginResult model returned by AuthService.authenticate()."""

    def test_instantiation_with_all_fields(self) -> None:
        """LoginResult should accept pysessid, access_token, and expires_in."""
        lr = LoginResult(pysessid="hex123", access_token="tok", expires_in=900)
        assert lr.pysessid == "hex123"
        assert lr.access_token == "tok"
        assert lr.expires_in == 900

    def test_serializes_to_dict(self) -> None:
        """Model must serialize to a dict with correct values."""
        lr = LoginResult(pysessid="abc", access_token="def", expires_in=300)
        d = lr.model_dump()
        assert d["pysessid"] == "abc"
        assert d["access_token"] == "def"
        assert d["expires_in"] == 300

    def test_rejects_missing_fields(self) -> None:
        """Creating without required fields should fail."""
        with pytest.raises(ValidationError):
            LoginResult(pysessid="abc")  # missing access_token, expires_in


# ── CurrentUser ──────────────────────────────────────────────────────────


class TestCurrentUser:
    """CurrentUser model returned by the get_current_user dependency."""

    def test_instantiation_with_all_fields(self) -> None:
        """CurrentUser should accept id, email, and permissions."""
        cu = CurrentUser(id=1, email="admin@site.com", permissions=["read"])
        assert cu.id == 1
        assert cu.email == "admin@site.com"
        assert cu.permissions == ["read"]

    def test_permissions_defaults_to_empty(self) -> None:
        """permissions should default to an empty list if not provided."""
        cu = CurrentUser(id=2, email="user@site.com", permissions=[])
        assert cu.permissions == []

    def test_serializes_to_dict(self) -> None:
        """Model must serialize to a dict with correct values."""
        cu = CurrentUser(id=3, email="test@site.com", permissions=["admin"])
        d = cu.model_dump()
        assert d["id"] == 3
        assert d["email"] == "test@site.com"
        assert d["permissions"] == ["admin"]

    def test_rejects_missing_fields(self) -> None:
        """Creating without id or email should fail."""
        with pytest.raises(ValidationError):
            CurrentUser(email="a@b.com", permissions=[])  # missing id
        with pytest.raises(ValidationError):
            CurrentUser(id=1)  # missing email
