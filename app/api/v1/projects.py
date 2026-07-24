from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresProjectService
from app.schemas.request.create_project import CreateProject
from app.schemas.request.update_project import UpdateProject
from app.schemas.response.list_response import ListResponse
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.project_response import ProjectResponse

router = APIRouter(prefix='/projects')


@router.get('/', response_model=ListResponse[ProjectResponse])
def list_projects(
    project_service: RequiresProjectService,
    limit: int | None = None,
    offset: int | None = None
):
    limit = min(max(1, limit), 50) if limit else 50
    offset = max(0, offset) if offset else 0

    projects = project_service.get_all(limit, offset, with_thumbnail=True)
    total = project_service.count()

    items = [ProjectResponse.from_model(p) for p in projects]

    return ListResponse(
        message='Projects found',
        items=items,
        meta={
            'total': total,
            'limit': limit,
            'offset': offset
        }
    )


@router.get('/{id}', response_model=ItemResponse[ProjectResponse])
def get_by_id(id: int, project_service: RequiresProjectService, current: RequiresAuth):
    if not current.user.can('read:project'):
        raise HTTPException(403, 'Forbidden.')

    project = project_service.get_by_id(id, with_thumbnail=True)

    if project is None:
        raise HTTPException(404, 'Project not found')

    return ItemResponse(message='Project found', item=ProjectResponse.from_model(project))


@router.post('/', status_code=201, response_model=ItemResponse[ProjectResponse])
def create_project(data: CreateProject, project_service: RequiresProjectService, current: RequiresAuth):
    if not current.user.can('write:project'):
        raise HTTPException(403, 'Forbidden.')

    project = project_service.create(data)
    return ItemResponse(message='Project saved.', item=ProjectResponse.from_model(project))


@router.patch('/{id}', response_model=ItemResponse[ProjectResponse])
def update_project(id: int, data: UpdateProject, project_service: RequiresProjectService, current: RequiresAuth):
    if not current.user.can('write:project'):
        raise HTTPException(403, 'Forbidden.')

    project = project_service.get_by_id(id)
    if not project:
        raise HTTPException(404, 'Project not found.')

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(project, key, value)

    result = project_service.update(project)
    return ItemResponse(message='Project updated.', item=ProjectResponse.from_model(result))


@router.delete('/{id}', status_code=204)
def destroy_project(id: int, project_service: RequiresProjectService, current: RequiresAuth):
    if not current.user.can('delete:project'):
        raise HTTPException(403, 'Forbidden.')
    result = project_service.delete(id)
    if not result:
        raise HTTPException(404, 'Project not found.')
