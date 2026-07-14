from datetime import datetime, timezone

from app.models.message import Message
from app.repositories.message_repository import MessageRepository
from app.services.static.email_service import EmailService
from app.services.static.templating_service import TemplatingService


class MessageService:
    msg_repo: MessageRepository
    email_service: type[EmailService]
    templating_service: type[TemplatingService]

    def __init__(
        self,
        msg_repo: MessageRepository,
        email_service: type[EmailService],
        templating_service: type[TemplatingService]
    ):
        self.msg_repo = msg_repo
        self.email_service = email_service
        self.templating_service = templating_service

    def get_all(self, limit: int | None = None, offset: int | None = None, unread: bool | None = None) -> list[Message]:
        return self.msg_repo.get_all(limit, offset, unread)

    def count_all(self, unread: bool | None = None) -> int:
        return self.msg_repo.count_all(unread)

    def get_by_id(self, id: int) -> Message | None:
        return self.msg_repo.get_by_id(id)
    
    def create(self, subject: str, mail_to: str, content: str) -> Message:
        message = Message(
            subject=subject,
            content=content,
            mail_to=mail_to,
            sent_at=datetime.now(timezone.utc)
        )

        return self.msg_repo.save(message)
    
    def read_now(self, id: int) -> Message | None:
        message = self.msg_repo.update(id, read_at=datetime.now(timezone.utc))
        return message
    
    def send_reply(self, message: Message) -> None:
        html = self.templating_service.render('reply-to-message.html.j2').using({
            'subject': message.subject,
            'content': message.content,
            'reply': message.reply,
        })

        self.email_service.send_html(message.mail_to, f'Re: {message.subject}', html)

    def reply_now(self, id: int, reply: str, uid: int) -> Message | None:
        now = datetime.now(timezone.utc)
        message = self.msg_repo.update(
            id,
            read_at=now,
            replied_at=now,
            replied_by=uid,
            reply=reply
        )

        if message is not None:
            try:
                self.send_reply(message)
            except Exception as e:
                print(f"Failed to send reply email for message {id}: {e}")

        return message
    
    def delete(self, id: int) -> bool:
        message = self.msg_repo.get_by_id(id)
        if message is None:
            return False
        if message.archived_at is not None:
            return False
        self.msg_repo.update(id, archived_at=datetime.now(timezone.utc))
        return True
