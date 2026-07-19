from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresProjectService
from app.schemas.request.create_project import CreateProject
from app.schemas.request.update_project import UpdateProject
from app.schemas.response.list_response import ListResponse
from app.schemas.response.item_response import ItemResponse
from app.models.project import Project

router = APIRouter(prefix='/projects')

@router.get('/', response_model=ListResponse[Project])
def list_projects(project_service: RequiresProjectService, current: RequiresAuth, limit: int | None = None, offset: int | None = None):
    try:
        if not current.user.can('read:project'):
            raise HTTPException(403, 'Forbidden.')
        limit = min(max(1, limit), 50) if limit else 50
        offset = max(0, offset) if offset else 0

        projects = project_service.get_all(limit, offset, with_thumbnail=True)
        total = project_service.count()

        return ListResponse(
            message='Projects found', 
            items=projects, 
            meta={
                'total': total, 
                'limit': limit, 
                'offset': offset
            }
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'An unknown error occurred while trying to list the projects.')


@router.get('/{id}', response_model=ItemResponse[Project])
def get_by_id(id: int, project_service: RequiresProjectService, current: RequiresAuth):
    try:
        if not current.user.can('read:project'):
            raise HTTPException(403, 'Forbidden.')
        
        project = project_service.get_by_id(id, with_thumbnail=True)

        if project is None:
            raise HTTPException(404, 'Project not found')
        
        return ItemResponse(message='Project found', item=project)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'An unknown error occurred while trying to retrieve the project.')


@router.post('/', response_model=ItemResponse[Project])
def create_project(data: CreateProject, project_service: RequiresProjectService, current: RequiresAuth):
    try:
        if not current.user.can('write:project'):
            raise HTTPException(403, 'Forbidden.')
        
        project = project_service.create(data)
        return ItemResponse(message='Project saved.', item=project)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'An unknown error occurred while trying to create the project.')


@router.patch('/{id}', response_model=ItemResponse[Project])
def update_project(id: int, data: UpdateProject, project_service: RequiresProjectService, current: RequiresAuth):
    try:
        if not current.user.can('write:project'):
            raise HTTPException(403, 'Forbidden.')
        
        project = project_service.get_by_id(id)
        if not project:
            raise HTTPException(404, 'Project not found.')
        
        if data.project_name is not None:
            project.project_name = data.project_name
        if data.project_lead is not None:
            project.project_lead = data.project_lead
        if data.summary is not None:
            project.summary = data.summary
        if data.description is not None:
            project.description = data.description
        if data.status is not None:
            project.status = data.status
        if data.tags is not None:
            project.tags = data.tags
        if data.thumbnail_url is not None:
            project.thumbnail_url = data.thumbnail_url

        result = project_service.update(project)
        return ItemResponse(message='Project updated.', item=result)

    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'An unknown error occurred while trying to update the project.')


@router.delete('/{id}', status_code=204)
def destroy_project(id: int, project_service: RequiresProjectService, current: RequiresAuth):
    try:
        if not current.user.can('delete:project'):
            raise HTTPException(403, 'Forbidden.')
        result = project_service.delete(id)
        if not result:
            raise HTTPException(404, 'Project not found.')
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'An unknown error occurred while trying to delete the project.')
