from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel  


class UpdateSelf(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    first_name: str | None
    last_name: str | None
    email: str | None
    profile_picture_url: str | None
    current_password: str