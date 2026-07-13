import smtplib
from email.message import EmailMessage
from app.config.settings import settings


class EmailService:
    @classmethod
    def send_text(cls, to_email: str, subject: str, content: str) -> None:
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = settings.smtp_from
        message['To'] = to_email
        message.set_content(content)

        cls._send(message)

    @classmethod
    def send_html(cls, to_email: str, subject: str, html: str) -> None:
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = settings.smtp_from
        message['To'] = to_email
        message.set_content(html, subtype='html')

        cls._send(message)

    @classmethod
    def _send(cls, message: EmailMessage) -> None:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_user and settings.smtp_pass.get_secret_value():
                smtp.starttls()
                smtp.login(settings.smtp_user, settings.smtp_pass.get_secret_value())
            smtp.send_message(message)
