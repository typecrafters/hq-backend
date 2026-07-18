from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class UpdateRole(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    name: str | None = None
    permissions: list[str] | None = None
    can_login: bool | None = None
