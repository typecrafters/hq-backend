from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.models.project import Project
from app.models.project import ProjectStatus


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_name: str
    project_lead: int
    status: ProjectStatus | None
    created_at: datetime
    updated_at: datetime | None
    tags: list[str]
    description: str | None
    summary: str
    thumbnail_url: str | None

    @classmethod
    def from_model(cls, project: Project | None):
        if project is None:
            return None
        return cls(
            id=project.id,
            project_name=project.project_name,
            project_lead=project.project_lead,
            status=project.status,
            created_at=project.created_at,
            updated_at=project.updated_at,
            tags=project.tags or [],
            description=project.description,
            summary=project.summary,
            thumbnail_url=project.thumbnail_url,
        )
