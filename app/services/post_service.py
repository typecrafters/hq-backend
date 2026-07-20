import re
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from app.models.post import Post, PostStatus
from app.repositories.post_repository import PostRepository
from app.schemas.internal.post_content import PostContent


_SLUG_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def _to_slug(value: str) -> str:
    slug = _SLUG_NORMALIZE_RE.sub("-", value.lower()).strip("-")
    return slug[:200] or "post"


def _ensure_unique_slug(repo: PostRepository, base: str, lang: str, exclude_id: int | None = None) -> str:
    slug = base
    suffix = 1
    while True:
        existing = repo.find_by_slug_and_lang(slug, lang)
        if existing is None or existing.id == exclude_id:
            return slug
        suffix += 1
        candidate = f"{base}-{suffix}"
        slug = candidate[:200]


def _dump_content(content: PostContent | dict | None) -> dict | None:
    if content is None:
        return None
    if isinstance(content, PostContent):
        data = content.model_dump()
        fm = data.get("front_matter") or {}
        if isinstance(fm.get("published_at"), datetime):
            fm["published_at"] = fm["published_at"].isoformat()
        return data
    return content


def _coerce_status(value: str | None) -> PostStatus | None:
    if not value:
        return None
    try:
        return PostStatus(value)
    except ValueError:
        return None


class PostService:
    post_repo: PostRepository

    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def get_all(self, limit: int | None = None, offset: int | None = None) -> list[Post]:
        return self.post_repo.get_all(limit, offset)

    def count_all(self) -> int:
        return self.post_repo.count()

    def get_by_id(self, id: int) -> Post | None:
        return self.post_repo.get_by_id(id)

    def create(
        self,
        title: str,
        author: int,
        content: dict | PostContent | None = None,
        status: str | None = None,
        featured: bool = False,
        slug: str | None = None,
        lang: str = "en",
    ) -> Post:
        base_slug = _to_slug(slug or title)
        unique_slug = _ensure_unique_slug(self.post_repo, base_slug, lang)

        post = Post(
            title=title,
            slug=unique_slug,
            lang=lang,
            author=author,
            content=_dump_content(content),
            status=_coerce_status(status),
            featured=featured,
            created_at=datetime.now(timezone.utc),
        )
        return self.post_repo.save(post)

    def update(
        self,
        id: int,
        title: str | None = None,
        content: dict | PostContent | None = None,
        status: str | None = None,
        featured: bool | None = None,
        slug: str | None = None,
        lang: str | None = None,
    ) -> Post | None:
        current = self.post_repo.get_by_id(id)
        if current is None:
            return None

        updates: dict = {}

        if title is not None:
            updates['title'] = title
        if slug is not None:
            current_lang = lang if lang is not None else current.lang
            base = _to_slug(slug)
            updates['slug'] = _ensure_unique_slug(self.post_repo, base, current_lang, exclude_id=id)
        if lang is not None:
            updates['lang'] = lang
        if content is not None:
            updates['content'] = _dump_content(content)
        if status is not None:
            coerced = _coerce_status(status)
            if coerced is not None:
                updates['status'] = coerced
        if featured is not None:
            updates['featured'] = featured

        updates['updated_at'] = datetime.now(timezone.utc)

        try:
            return self.post_repo.update(id, **updates)
        except IntegrityError:
            return None

    def delete(self, id: int) -> bool:
        post = self.post_repo.get_by_id(id)
        if post is None:
            return False
        self.post_repo.delete(post)
        return True
