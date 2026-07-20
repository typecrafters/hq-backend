from datetime import datetime
from typing import Self
from pydantic import BaseModel, ConfigDict
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.response.user_response import UserResponse

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_name: str
    lead: UserResponse
    status: ProjectStatus | None
    created_at: datetime
    updated_at: datetime | None
    tags: list[str]
    description: str | None
    summary: str
    thumbnail_url: str | None

    @classmethod
    def from_model(cls, model: Project, lead: User) -> Self:
        return cls(
            id=model.id,
            project_name=model.project_name,
            lead=UserResponse.from_model(lead),
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
            description=model.description,
            summary=model.summary,
            thumnail_url=model.thumbnail_url
        )