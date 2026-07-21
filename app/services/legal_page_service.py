from datetime import datetime, timezone

from app.models.legal_page import LegalPage
from app.repositories.legal_page_repository import LegalPageRepository


class LegalPageService:
    legal_page_repo: LegalPageRepository

    def __init__(self, legal_page_repo: LegalPageRepository):
        self.legal_page_repo = legal_page_repo

    def get_by_slug(self, slug: str) -> LegalPage | None:
        return self.legal_page_repo.find_by_slug(slug)

    def get_or_create(self, slug: str) -> LegalPage:
        page = self.legal_page_repo.find_by_slug(slug)
        if page is None:
            page = LegalPage(
                slug=slug,
                title=slug.replace('-', ' ').title(),
                content_markdown='',
            )
            page = self.legal_page_repo.save(page)
        return page

    def update(self, slug: str, title: str | None = None, content_markdown: str | None = None) -> LegalPage | None:
        page = self.legal_page_repo.find_by_slug(slug)
        if page is None:
            return None

        if title is not None:
            page.title = title
        if content_markdown is not None:
            page.content_markdown = content_markdown
        page.updated_at = datetime.now(timezone.utc)

        return self.legal_page_repo.save(page)
