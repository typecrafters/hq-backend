from enum import StrEnum


class TokenType(StrEnum):
    EmailVerification = "email_verification"
    PasswordReset = "password_reset"