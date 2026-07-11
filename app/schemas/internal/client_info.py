from pydantic import BaseModel


class ClientInfo(BaseModel):
    ip_address: str
    user_agent: str