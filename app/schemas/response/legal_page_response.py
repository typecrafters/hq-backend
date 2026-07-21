from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LegalPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    content_markdown: str
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_model(cls, page):
        if page is None:
            return None
        return cls(
            id=page.id,
            slug=page.slug,
            title=page.title,
            content_markdown=page.content_markdown,
            created_at=page.created_at,
            updated_at=page.updated_at,
        )
