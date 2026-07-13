"""Static JWT encode/decode service.

Follows the same static-class pattern as CryptoService and PasswordService
in this package — reads settings directly, no DI, no DB dependency.
"""

import jwt

from app.config.settings import settings


class JwtService:
    """Stateless JWT encoder / decoder.

    Usage
    -----
    >>> token = JwtService.encode({"sub": 1, "email": "a@b.com"})
    >>> claims = JwtService.decode(token)
    """

    _secret: str = settings.jwt_secret.get_secret_value()
    _algorithm: str = settings.jwt_algorithm

    @classmethod
    def encode(cls, payload: dict) -> str:
        """Return a signed JWT string for *payload*.

        The caller is responsible for including ``iat``, ``exp``, and any
        other required claims in *payload* before calling ``encode()``.
        """
        return jwt.encode(payload, cls._secret, algorithm=cls._algorithm)

    @classmethod
    def decode(cls, token: str) -> dict:
        """Decode and validate *token*, returning the claims dict.

        Raises
        ------
        jwt.PyJWTError
            If the signature is invalid, the token is expired, or the
            algorithm doesn't match.
        """
        return jwt.decode(token, cls._secret, algorithms=[cls._algorithm])
