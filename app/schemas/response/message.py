from datetime import datetime
from pydantic import BaseModel, ConfigDict, computed_field

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    content: str
    mail_to: str
    sent_at: datetime
    read_at: datetime | None
    replied_at: datetime | None
    replied_by: int | None
    reply: str | None
    archived_at: datetime | None

    @computed_field
    @property
    def status(self) -> str:
        if self.read_at is None:
            return 'Received'
        if self.replied_at is None:
            return 'Read'
        return 'Replied'
