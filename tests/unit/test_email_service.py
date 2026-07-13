"""Unit tests for EmailService.

Mocks ``smtplib.SMTP`` so no real mail server is needed.
"""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from app.services.static.email_service import EmailService


class TestEmailService:
    """Covers EmailService.send_password_reset_email and _send."""

    @patch("app.services.static.email_service.smtplib.SMTP")
    def test_send_password_reset_email_creates_message(self, mock_smtp):
        """Verify the message is built with correct To/Subject/content."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        EmailService.send_password_reset_email(
            to_email="user@example.com",
            reset_link="https://example.com/reset?token=abc123",
        )

        mock_smtp.assert_called_once()
        mock_server.send_message.assert_called_once()
        msg = mock_server.send_message.call_args[0][0]
        assert msg["To"] == "user@example.com"
        assert msg["Subject"] == "Reset your password"
        assert "reset your password" in msg.get_content().lower()

    @patch("app.services.static.email_service.smtplib.SMTP")
    def test_send_password_reset_without_auth(self, mock_smtp):
        """When SMTP credentials are empty, no TLS/login is attempted."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # conftest sets SMTP_HOST="" and SMTP_PORT=0, so
        # smtplib.SMTP("", 0) is called but mocked — no crash.
        EmailService.send_password_reset_email(
            to_email="a@b.com",
            reset_link="http://localhost/reset",
        )

        mock_server.starttls.assert_not_called()
        mock_server.login.assert_not_called()

    @patch("app.services.static.email_service.smtplib.SMTP")
    def test_send_password_reset_with_auth(self, mock_smtp):
        """When SMTP credentials are set, TLS and login are called."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        secret = SecretStr("hunter2")
        with patch("app.services.static.email_service.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.test.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_user = "testuser"
            mock_settings.smtp_pass = secret
            mock_settings.smtp_from = "noreply@test.com"

            EmailService.send_password_reset_email(
                to_email="b@c.com",
                reset_link="http://localhost/reset",
            )

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("testuser", "hunter2")
