from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CreatePost(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str
    content: dict | None = None
    status: str | None = None
    featured: bool = False
