from datetime import datetime, timezone
from app.schemas.request.create_project import CreateProject
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.services.static.file_service import FileService


class ProjectService:
    project_repo: ProjectRepository
    file_service: type[FileService]

    def __init__(self, project_repo: ProjectRepository, file_service: type[FileService]):
        self.project_repo = project_repo
        self.file_service = file_service

    def get_all(self, limit: int | None = None, offset: int | None = None, with_thumbnail: bool = False) -> list[Project]:
        projects = self.project_repo.get_all(limit, offset)

        if with_thumbnail:
            for project in projects:
                self.project_repo.db.expunge(project)
                project.thumbnail_url = self.file_service.sign_get(project.thumbnail_url)

        return projects

    def count(self) -> int:
        return self.project_repo.count()

    def get_by_id(self, id: int, with_thumbnail: bool = False) -> Project | None:
        project = self.project_repo.get_by_id(id)
        if project is None:
            return None
        if with_thumbnail:
            self.project_repo.db.expunge(project)
            project.thumbnail_url = self.file_service.sign_get(project.thumbnail_url)
        return project

    def create(
        self,
        data: CreateProject
    ) -> Project:
        tags = list(set(data.tags))
        now = datetime.now(timezone.utc)

        project = Project(
            project_name=data.project_name,
            project_lead=data.project_lead,
            status=data.status,
            created_at=now,
            tags=tags,
            description=data.description,
            summary=data.summary,
            thumbnail_url=data.thumbnail_url,
        )

        return self.project_repo.save(project)

    def update(self, project: Project) -> Project | None:
        if self.project_repo.exists(project.id):
            return self.project_repo.save(project)

    def delete(self, id: int) -> bool:
        project = self.project_repo.get_by_id(id)
        if project is None:
            return False
        self.project_repo.delete_by_id(id)
        return True

