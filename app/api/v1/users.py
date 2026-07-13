from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresPasswordService, RequiresUserService
from app.schemas.request.create_user import CreateUser
from app.schemas.request.update_self import UpdateSelf
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.user_with_role import UserWithRole

router = APIRouter(prefix='/users')

@router.get('/')
def list_users(page: int, limit: int, user_service: RequiresUserService):
    return user_service.list(page, limit)

@router.post('/')
def save_user(user: CreateUser, user_service: RequiresUserService):
    return user_service.create(user)

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

        if not user.profile_picture_url and not data.profile_picture_url:
            pass  # Wanna be startin' somethin'

        user_service.update(user)

        updated = user_service.load_by_id(user.id, with_picture=True)

        return ItemResponse(message='User updated successfully', item=updated)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while updating the user.')

