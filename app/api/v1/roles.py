from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresRoleRepository
from app.schemas.request.update_role import UpdateRole
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.role_response import RoleResponse


router = APIRouter(prefix='/roles')


@router.patch('/{id}', status_code=200, response_model=ItemResponse[RoleResponse])
def update_role(id: int, data: UpdateRole, current: RequiresAuth, role_repo: RequiresRoleRepository):
    try:
        if not current.user.can('write:role'):
            raise HTTPException(403, 'Forbidden.')

        role = role_repo.get_by_id(id)
        if not role:
            raise HTTPException(404, 'Role not found.')

        if data.name is not None:
            role.name = data.name
        if data.permissions is not None:
            role.permissions = data.permissions
        if data.can_login is not None:
            role.can_login = data.can_login

        role_repo.save(role)

        item = RoleResponse.from_model(role)
        return ItemResponse(message='Role updated successfully', item=item)
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(500, 'An unknown error occurred while updating the role.')
