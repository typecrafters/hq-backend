from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict

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