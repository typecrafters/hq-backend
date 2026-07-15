from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class UpdateUser(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    email: str | None = None
    role_id: int | None = None
    profile_picture_url: str | None = None
    show_on_page: bool | None = None
    password: str | None = None
