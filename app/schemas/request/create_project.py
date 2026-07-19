from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from app.models.project import ProjectStatus

class CreateProject(BaseModel): 
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    project_name: str
    project_lead: int | None = None
    summary: str
    description: str | None = None
    status: ProjectStatus
    tags: list[str]
    thumbnail_url: str | None = None