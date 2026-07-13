"""Tests for JWT settings configuration and PyJWT import (Task 1.1)."""

from pydantic import SecretStr

from app.config.settings import Settings


class TestJwtSettings:
    """JWT-specific settings fields must load and default correctly."""

    def test_algorithm_defaults_to_hs256(self) -> None:
        """jwt_algorithm should default to 'HS256'."""
        s = Settings(jwt_secret="custom-secret")
        assert s.jwt_algorithm == "HS256"

    def test_expiry_defaults_to_15_minutes(self) -> None:
        """jwt_expiry_minutes should default to 15."""
        s = Settings(jwt_secret="custom-secret")
        assert s.jwt_expiry_minutes == 15

    def test_jwt_secret_is_secret_str(self) -> None:
        """jwt_secret must be stored as a SecretStr for secure handling."""
        s = Settings(jwt_secret="my-secret-key")
        assert isinstance(s.jwt_secret, SecretStr)
        assert s.jwt_secret.get_secret_value() == "my-secret-key"

    def test_can_override_algorithm(self) -> None:
        """jwt_algorithm should be overridable via constructor."""
        s = Settings(jwt_secret="s", jwt_algorithm="RS256")
        assert s.jwt_algorithm == "RS256"

    def test_can_override_expiry(self) -> None:
        """jwt_expiry_minutes should be overridable via constructor."""
        s = Settings(jwt_secret="s", jwt_expiry_minutes=30)
        assert s.jwt_expiry_minutes == 30


class TestPyJwtImport:
    """PyJWT library must be available as a project dependency."""

    def test_jwt_module_has_encode_decode(self) -> None:
        """jwt.encode and jwt.decode should be callable."""
        import jwt

        assert callable(jwt.encode)
        assert callable(jwt.decode)

    def test_jwt_has_pyjwterror(self) -> None:
        """jwt.PyJWTError should exist for exception handling."""
        import jwt

        assert jwt.PyJWTError is not None
        assert issubclass(jwt.PyJWTError, Exception)
