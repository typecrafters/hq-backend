from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CreateUser(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    
    first_name: str
    last_name: str
    title: str
    email: str
    password: str
    permissions: list[str]
    can_access_panel: bool
    show_on_page: bool
    profile_picture_url: str