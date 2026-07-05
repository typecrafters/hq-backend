from pydantic import BaseModel, ConfigDict

class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    permissions: list[str]
    can_login: bool
