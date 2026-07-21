from sqlalchemy.orm import Session

from app.models.legal_page import LegalPage
from app.repositories.repository import Repository


class LegalPageRepository(Repository[LegalPage, int]):
    def __init__(self, db: Session):
        super().__init__(db, LegalPage)

    def find_by_slug(self, slug: str) -> LegalPage | None:
        from sqlalchemy import select
        stmt = select(self.entity).where(self.entity.slug == slug)
        return self.db.execute(stmt).scalar_one_or_none()
