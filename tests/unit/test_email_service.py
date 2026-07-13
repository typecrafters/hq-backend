"""Unit tests for EmailService.

Mocks ``smtplib.SMTP`` so no real mail server is needed.
"""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

from app.services.static.email_service import EmailService


class TestEmailService:
    """Covers EmailService.send_text, send_html, and _send."""

    @patch("app.services.static.email_service.smtplib.SMTP")
    def test_send_text_creates_message(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        EmailService.send_text(
            to_email="user@example.com",
            subject="Hello",
            content="Hello there",
        )

        mock_smtp.assert_called_once()
        mock_server.send_message.assert_called_once()
        msg = mock_server.send_message.call_args[0][0]
        assert msg["To"] == "user@example.com"
        assert msg["Subject"] == "Hello"
        assert "Hello there" in msg.get_content()

    @patch("app.services.static.email_service.smtplib.SMTP")
    def test_send_html_creates_message(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        EmailService.send_html(
            to_email="user@example.com",
            subject="HTML Mail",
            html="<h1>Hi</h1>",
        )

        mock_server.send_message.assert_called_once()
        msg = mock_server.send_message.call_args[0][0]
        assert msg["Subject"] == "HTML Mail"
        assert "<h1>Hi</h1>" in msg.get_content()

    @patch("app.services.static.email_service.smtplib.SMTP")
    def test_send_without_smtp_auth(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        EmailService.send_text(
            to_email="a@b.com",
            subject="Test",
            content="body",
        )

        mock_server.starttls.assert_not_called()
        mock_server.login.assert_not_called()

    @patch("app.services.static.email_service.smtplib.SMTP")
    def test_send_with_smtp_auth(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        secret = SecretStr("hunter2")
        with patch("app.services.static.email_service.settings") as mock_settings:
            mock_settings.smtp_host = "smtp.test.com"
            mock_settings.smtp_port = 587
            mock_settings.smtp_user = "testuser"
            mock_settings.smtp_pass = secret
            mock_settings.smtp_from = "noreply@test.com"

            EmailService.send_text(
                to_email="b@c.com",
                subject="Auth Test",
                content="secret",
            )

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("testuser", "hunter2")
