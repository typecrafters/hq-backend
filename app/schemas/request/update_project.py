from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from app.models.project import ProjectStatus

class UpdateProject(BaseModel): 
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    project_name: str | None = None
    project_lead: int | None = None
    summary: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    tags: list[str] | None = None
    thumbnail_url: str | None = None