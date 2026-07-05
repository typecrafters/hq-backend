from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.repository import Repository

class ProjectRepository(Repository[Project, int]):
    def __init__(self, db: Session):
        super().__init__(db, Project)
