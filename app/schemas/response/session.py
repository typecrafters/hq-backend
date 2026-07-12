from datetime import datetime
from typing import Any, Self
from pydantic import BaseModel, ConfigDict
from app.models.session import Session as SessionModel
class Session(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    uid: int
    ip_address: str
    user_agent: str
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    data: dict[str, Any]

    @classmethod
    def from_model(cls, model: SessionModel) -> Self:
        return cls(
            id = model.id,
            uid = model.uid,
            ip_address = model.ip_address,
            user_agent = model.user_agent,
            issued_at = model.issued_at,
            expires_at = model.expires_at,
            revoked_at = model.revoked_at,
            data = model.data
        )