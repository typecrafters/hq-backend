"""Auth-related response schemas for JWT token responses."""

from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    """Response body returned on successful login and refresh.

    Serializes to JSON with camelCase field names for the API consumer.
    Snake-case Python names (``access_token``) also work for construction.
    """

    model_config = ConfigDict(populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")


class LoginResult(BaseModel):
    """Internal result returned by AuthService.authenticate().

    Contains both the new pysessid session identifier and the JWT access
    token so the route handler can set the cookie and return the JSON body.
    """

    model_config = ConfigDict(populate_by_name=True)

    pysessid: str
    access_token: str = Field(alias="accessToken")
    expires_in: int = Field(alias="expiresIn")
