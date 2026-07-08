import smtplib
from email.message import EmailMessage
from app.config.settings import settings


class EmailService:
    @classmethod
    def send_password_reset_email(cls, to_email: str, reset_link: str) -> None:
        message = EmailMessage()
        message['Subject'] = 'Reset your password'
        message['From'] = settings.smtp_from
        message['To'] = to_email
        message.set_content(
            'We received a request to reset your password.\n\n'
            f'Click the link below to choose a new password:\n{reset_link}\n\n'
            "If you didn't request this, you can safely ignore this email."
        )

        cls._send(message)

    @classmethod
    def _send(cls, message: EmailMessage) -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_user and settings.smtp_pass.get_secret_value():
                smtp.starttls()
                smtp.login(settings.smtp_user, settings.smtp_pass.get_secret_value())
            smtp.send_message(message)
