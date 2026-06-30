from typing import Annotated
from fastapi import Depends
from app.services.crypto_service import CryptoService
from app.services.password_service import PasswordService


def password_service() -> type[PasswordService]:
    return PasswordService

RequiresPasswordService = Annotated[type[PasswordService], Depends(password_service)]


def crypto_service() -> type[CryptoService]:
    return CryptoService

RequiresCryptoService = Annotated[type[PasswordService], Depends(crypto_service)]