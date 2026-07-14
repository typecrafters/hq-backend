from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresPasswordService, RequiresUserService
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.list_response import ListResponse
from app.schemas.request.create_user import CreateUser
from app.schemas.request.update_self import UpdateSelf
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.user_with_role import UserWithRole
from app.schemas.response.user_response import UserResponse

router = APIRouter(prefix='/users')

@router.get('/', response_model=ListResponse[UserResponse])
def list_users(
    page: int,
    limit: int,
    user_service: RequiresUserService
):
    result = user_service.list(page, limit, with_picture=True)
    payload = [UserResponse.from_model(u) for u in result]
    return ListResponse(message='Users retrieved', items=payload, meta={ 'count': len(payload) })

@router.post('/', status_code=201, response_model=ItemResponse[UserResponse])
def save_user(
    user: CreateUser,
    user_service: RequiresUserService,
    current_user: RequiresAuth,
):
    result = user_service.create(user)
    item = UserResponse.from_model(result)
    return ItemResponse(message='User created successfully', item=item)

@router.patch('/me', status_code=200, response_model=ItemResponse[UserWithRole])
def update_self(
    data: UpdateSelf,
    current: RequiresAuth,
    user_service: RequiresUserService,
    password_service: RequiresPasswordService
):
    try:
        user = user_service.get_by_id(current.user.id)
        if not user:
            raise HTTPException(403, 'Forbidden.')

        if user.password is None or not password_service.compare(user.password, data.current_password):
            raise HTTPException(401, 'Incorrect password.')

        if data.email and data.email != user.email:
            existing = user_service.get_by_email(data.email)
            if existing and existing.id != user.id:
                raise HTTPException(409, 'Email already in use.')
            user.email = data.email
        if data.first_name:
            user.first_name = data.first_name
        if data.last_name:
            user.last_name = data.last_name
        if data.profile_picture_url:
            user.profile_picture_url = data.profile_picture_url
        if data.password:
            user.password = password_service.hash(data.password)

        if not user.profile_picture_url and not data.profile_picture_url:
            pass  # Wanna be startin' somethin'

        user_service.update(user)

        updated = user_service.load_by_id(user.id, with_picture=True)

        return ItemResponse(message='User updated successfully', item=updated)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while updating the user.')

