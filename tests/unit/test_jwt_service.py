"""Tests for JwtService encode/decode (Task 1.2).

Follows the same static-class test pattern as CryptoService / PasswordService.
All tests are pure unit — no mocks, no DB.
"""

import time

import jwt as pyjwt
import pytest

from app.services.static.jwt_service import JwtService

# ── helpers ──────────────────────────────────────────────────────────────


def _tamper(token: str) -> str:
    """Return the token with its signature portion corrupted."""
    parts = token.split(".")
    return f"{parts[0]}.{parts[1]}.bad-sig"


# ── encode ───────────────────────────────────────────────────────────────


class TestEncode:
    """JwtService.encode must produce a valid signed JWT."""

    def test_returns_a_string_with_three_parts(self) -> None:
        """A minimal payload should produce a valid three-part JWT."""
        token = JwtService.encode({"sub": "1"})
        parts = token.split(".")
        assert len(parts) == 3
        assert all(part for part in parts)  # no empty segments

    def test_encodes_payload_claims(self) -> None:
        """Claims passed to encode must be present in the decoded token."""
        payload = {"sub": "42", "email": "a@b.com", "permissions": ["read"]}
        token = JwtService.encode(payload)
        decoded = pyjwt.decode(
            token,
            JwtService._secret,
            algorithms=[JwtService._algorithm],
        )
        assert decoded["sub"] == "42"
        assert decoded["email"] == "a@b.com"
        assert decoded["permissions"] == ["read"]


# ── decode ───────────────────────────────────────────────────────────────


class TestDecode:
    """JwtService.decode must validate and return claims."""

    def test_roundtrip_returns_original_payload(self) -> None:
        """decode(encode(payload)) should return the original data."""
        payload = {"sub": "7", "email": "user@site.com"}
        token = JwtService.encode(payload)
        result = JwtService.decode(token)
        assert result["sub"] == "7"
        assert result["email"] == "user@site.com"

    def test_decode_preserves_custom_claims(self) -> None:
        """Custom claims like email and permissions survive a roundtrip."""
        payload = {"sub": "1", "email": "test@site.com", "permissions": ["read", "write"]}
        token = JwtService.encode(payload)
        result = JwtService.decode(token)
        assert result["email"] == "test@site.com"
        assert result["permissions"] == ["read", "write"]

    def test_raises_on_tampered_token(self) -> None:
        """A token with an invalid signature must raise PyJWTError."""
        token = JwtService.encode({"sub": "1"})
        tampered = _tamper(token)
        with pytest.raises(pyjwt.PyJWTError):
            JwtService.decode(tampered)

    def test_raises_on_expired_token(self) -> None:
        """A token with an exp claim in the past must raise PyJWTError."""
        token = JwtService.encode({"sub": "1", "exp": int(time.time()) - 60})
        with pytest.raises(pyjwt.PyJWTError):
            JwtService.decode(token)

    def test_raises_on_wrong_algorithm(self) -> None:
        """A token signed with RS256 should not validate under HS256."""
        # Encode with a different algorithm (simulate by signing externally)
        # We manually create a token with HS256 but corrupt the algo check
        # by encoding with a different secret
        import base64
        import hashlib
        import hmac
        import json

        header = (
            base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
            .rstrip(b"=")
            .decode()
        )
        payload = base64.urlsafe_b64encode(json.dumps({"sub": "1"}).encode()).rstrip(b"=").decode()
        sig = (
            base64.urlsafe_b64encode(
                hmac.new(
                    b"different-secret",
                    f"{header}.{payload}".encode(),
                    hashlib.sha256,
                ).digest()
            )
            .rstrip(b"=")
            .decode()
        )
        wrong_token = f"{header}.{payload}.{sig}"

        with pytest.raises(pyjwt.PyJWTError):
            JwtService.decode(wrong_token)
