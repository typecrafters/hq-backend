"""Post content schema — block-based content with front-matter, Hexo-style.

`PostContent` is a JSONB blob stored in `posts.content` with this shape:

    {
        "blocks": [<Block>, ...],
        "front_matter": {
            "excerpt": "...",
            "cover_image_url": "...",
            "categories": ["Tech", "Backend"],
            "lang": "en" | "es",
            "published_at": "2026-07-20T12:00:00Z"
        }
    }

`blocks` is a list of discriminated blocks. The `type` field is the
discriminator; any unknown value will be rejected by pydantic.
"""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


Lang = Literal["en", "es"]


class FrontMatter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    excerpt: Annotated[str, StringConstraints(max_length=500)] | None = None
    cover_image_url: str | None = None
    categories: list[Annotated[str, StringConstraints(min_length=1, max_length=64)]] = Field(
        default_factory=list, max_length=8
    )
    lang: Lang = "en"
    published_at: datetime | None = None


class _BlockBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ParagraphBlock(_BlockBase):
    type: Literal["paragraph"]
    text: Annotated[str, StringConstraints(min_length=1, max_length=10_000)]


class HeadingBlock(_BlockBase):
    type: Literal["heading"]
    level: Literal[1, 2, 3, 4, 5, 6]
    text: Annotated[str, StringConstraints(min_length=1, max_length=500)]


class ImageBlock(_BlockBase):
    type: Literal["image"]
    url: Annotated[str, StringConstraints(min_length=1, max_length=2_000)]
    alt: Annotated[str, StringConstraints(max_length=500)] = ""
    caption: Annotated[str, StringConstraints(max_length=500)] = ""


class CodeBlock(_BlockBase):
    type: Literal["code"]
    language: Annotated[str, StringConstraints(min_length=1, max_length=64)] = "text"
    code: Annotated[str, StringConstraints(max_length=50_000)]


class QuoteBlock(_BlockBase):
    type: Literal["quote"]
    text: Annotated[str, StringConstraints(min_length=1, max_length=2_000)]
    cite: Annotated[str, StringConstraints(max_length=500)] = ""


class ListBlock(_BlockBase):
    type: Literal["list"]
    ordered: bool = False
    items: list[Annotated[str, StringConstraints(min_length=1, max_length=1_000)]] = Field(
        min_length=1, max_length=200
    )


class EmbedBlock(_BlockBase):
    type: Literal["embed"]
    url: Annotated[str, StringConstraints(min_length=1, max_length=2_000)]
    provider: Annotated[str, StringConstraints(max_length=64)] = ""


class DividerBlock(_BlockBase):
    type: Literal["divider"]


Block = Annotated[
    ParagraphBlock
    | HeadingBlock
    | ImageBlock
    | CodeBlock
    | QuoteBlock
    | ListBlock
    | EmbedBlock
    | DividerBlock,
    Field(discriminator="type"),
]


class PostContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blocks: list[Block] = Field(min_length=1, max_length=500)
    front_matter: FrontMatter = Field(default_factory=FrontMatter)
