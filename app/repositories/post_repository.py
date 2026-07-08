from sqlalchemy.orm import Session

from app.models.post import Post
from app.repositories.repository import Repository

class PostRepository(Repository[Post, int]):
    def __init__(self, db: Session):
        super().__init__(db, Post)
