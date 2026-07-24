from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresRoleRepository
from app.schemas.request.update_role import UpdateRole
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.role_response import RoleResponse


router = APIRouter(prefix='/roles')


@router.patch('/{id}', status_code=200, response_model=ItemResponse[RoleResponse])
def update_role(id: int, data: UpdateRole, current: RequiresAuth, role_repo: RequiresRoleRepository):
    if not current.user.can('write:role'):
        raise HTTPException(403, 'Forbidden.')

    role = role_repo.get_by_id(id)
    if not role:
        raise HTTPException(404, 'Role not found.')

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(role, key, value)

    role_repo.save(role)

    item = RoleResponse.from_model(role)
    return ItemResponse(message='Role updated successfully', item=item)
