from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.post import PostStatus


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    lang: str
    author: int
    status: str | None
    created_at: datetime
    updated_at: datetime | None
    content: dict | None
    featured: bool

    @classmethod
    def from_model(cls, post):
        if post is None:
            return None
        return cls(
            id=post.id,
            title=post.title,
            slug=post.slug,
            lang=post.lang,
            author=post.author,
            status=post.status.value if post.status else None,
            created_at=post.created_at,
            updated_at=post.updated_at,
            content=post.content,
            featured=post.featured,
        )
