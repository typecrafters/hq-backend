from sqlalchemy.orm import Session

from app.models.post import Post
from app.repositories.repository import Repository

class PostRepository(Repository[Post, int]):
    def __init__(self, db: Session):
        super().__init__(db, Post)

    def find_by_slug_and_lang(self, slug: str, lang: str) -> Post | None:
        from sqlalchemy import select
        stmt = select(self.entity).where(self.entity.slug == slug, self.entity.lang == lang)
        return self.db.execute(stmt).scalar_one_or_none()
