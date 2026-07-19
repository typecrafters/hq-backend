from datetime import datetime, timezone

from app.models.post import Post, PostStatus
from app.repositories.post_repository import PostRepository


class PostService:
    post_repo: PostRepository

    def __init__(self, post_repo: PostRepository):
        self.post_repo = post_repo

    def get_all(self, limit: int | None = None, offset: int | None = None) -> list[Post]:
        return self.post_repo.get_all(limit, offset)

    def count_all(self) -> int:
        return self.post_repo.count_all()

    def get_by_id(self, id: int) -> Post | None:
        return self.post_repo.get_by_id(id)

    def create(self, title: str, author: int, content: dict | None = None, status: str | None = None, featured: bool = False) -> Post:
        post_status = None
        if status:
            try:
                post_status = PostStatus(status)
            except ValueError:
                pass

        post = Post(
            title=title,
            author=author,
            content=content,
            status=post_status,
            featured=featured,
            created_at=datetime.now(timezone.utc),
        )
        return self.post_repo.save(post)

    def update(self, id: int, title: str | None = None, content: dict | None = None, status: str | None = None, featured: bool | None = None) -> Post | None:
        updates = {}

        if title is not None:
            updates['title'] = title
        if content is not None:
            updates['content'] = content
        if status is not None:
            try:
                updates['status'] = PostStatus(status)
            except ValueError:
                pass
        if featured is not None:
            updates['featured'] = featured

        updates['updated_at'] = datetime.now(timezone.utc)

        return self.post_repo.update(id, **updates)

    def delete(self, id: int) -> bool:
        post = self.post_repo.get_by_id(id)
        if post is None:
            return False
        self.post_repo.delete(post)
        return True
