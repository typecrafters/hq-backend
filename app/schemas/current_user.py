"""Lightweight stateless user model extracted from a validated JWT."""

from pydantic import BaseModel


class CurrentUser(BaseModel):
    """Represents the authenticated user derived from a Bearer JWT token.

    Unlike :class:`app.schemas.current.Current`, this model is stateless —
    it contains no session data and is built solely from JWT claims. Routes
    that need the full user profile perform a separate DB lookup.
    """

    id: int
    email: str
    permissions: list[str] = []
