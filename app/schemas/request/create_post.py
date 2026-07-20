from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.schemas.internal.post_content import PostContent


class CreatePost(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    title: str
    slug: str | None = None
    lang: str = "en"
    content: PostContent | None = None
    status: str | None = None
    featured: bool = False
