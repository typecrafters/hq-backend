from pydantic import BaseModel, ConfigDict
from app.models.role import Role as RoleModel

class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    permissions: list[str]
    can_login: bool

    @classmethod
    def from_model(cls, role: RoleModel | None):
        if role is None:
            return None
        return cls(
            id=role.id,
            name=role.name,
            permissions=role.permissions,
            can_login=role.can_login
        )