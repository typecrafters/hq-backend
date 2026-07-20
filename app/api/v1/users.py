from fastapi import APIRouter, HTTPException
from app.dependencies import RequiresAuth, RequiresPasswordService, RequiresUserService, RequiresAuthService, RequiresSessionRepository
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.list_response import ListResponse
from app.schemas.request.create_user import CreateUser
from app.schemas.request.update_self import UpdateSelf
from app.schemas.request.update_user import UpdateUser
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.user_with_role import UserWithRole
from app.schemas.response.user_response import UserResponse
from app.schemas.response.session import Session

router = APIRouter(prefix='/users')


@router.get('/', response_model=ListResponse[UserResponse])
def list_users(
    current: RequiresAuth,
    user_service: RequiresUserService,
    page: int | None = None,
    limit: int | None = None
):
    if not current.user.can('read:user'):
        raise HTTPException(403, 'Forbidden.')
    if not page:
        page = 1
    if not limit:
        limit = 100
    result = user_service.list(page, limit, with_picture=True)
    payload = [UserResponse.from_model(u) for u in result]
    return ListResponse(message='Users retrieved', items=payload, meta={'count': len(payload)})

@router.get('/{id}', response_model=ItemResponse[UserWithRole])
def get_by_id(
    id: int,
    current: RequiresAuth,
    user_service: RequiresUserService
):
    try:
        if not current.user.can('read:user'):
            raise HTTPException(403, 'Forbidden.')
        result = user_service.load_by_id(id, with_picture=True)
        if result is None:
            raise HTTPException(404, 'User not found.')
        return ItemResponse(message='User retrieved successfully', item=result)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, 'An unknown error occurred while retrieving the user.')

@router.get('/{id}/sessions', response_model=ListResponse[Session])
def get_user_sessions(
    id: int,
    current: RequiresAuth,
    session_repo: RequiresSessionRepository
):
    try:
        if not current.user.can('write:user'):
            raise HTTPException(403, 'Forbidden.')
        sessions = [Session.from_model(s) for s in session_repo.get_all_by_uid(id)]
        return ListResponse(message='Session list found', items=sessions, meta={'count': len(sessions)})
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, 'An unknown error occurred while retrieving sessions.')

@router.delete('/{id}/sessions/{hash}', status_code=204)
def revoke_user_session(
    id: int,
    hash: str,
    current: RequiresAuth,
    session_repo: RequiresSessionRepository
):
    try:
        if not current.user.can('write:user'):
            raise HTTPException(403, 'Forbidden.')

        session = session_repo.for_user_by_hash(id, hash)
        if session is None:
            raise HTTPException(404, 'Session not found.')

        session_repo.delete_by_id(session.id)
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, 'An unknown error occurred while revoking the session.')

@router.post('/', status_code=201, response_model=ItemResponse[UserResponse])
def save_user(
    user: CreateUser,
    user_service: RequiresUserService,
    current: RequiresAuth
):
    try:
        if not current.user.can('write:user'):
            raise HTTPException(403, 'Forbidden.')
        result = user_service.create(user)
        user_service.create_email_verification_token(result)
        item = UserResponse.from_model(result)
        return ItemResponse(message='User created successfully', item=item)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, 'An unknown error occurred while updating the user.')


@router.patch('/me', status_code=200, response_model=ItemResponse[UserWithRole])
def update_self(
    data: UpdateSelf,
    current: RequiresAuth,
    user_service: RequiresUserService,
    password_service: RequiresPasswordService
):
    try:
        if not current.user.can('write:user'):
            raise HTTPException(403, 'Forbidden.')
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
            user.profile_picture_url = 'system/placeholder.svg'

        user_service.update(user)

        updated = user_service.load_by_id(user.id, with_picture=True)

        return ItemResponse(message='User updated successfully', item=updated)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, 'An unknown error occurred while updating the user.')

@router.patch('/{id}', status_code=200, response_model=ItemResponse[UserWithRole])
def update_user(
    id: int,
    data: UpdateUser,
    current: RequiresAuth,
    user_service: RequiresUserService,
    password_service: RequiresPasswordService
):
    try:
        if not current.user.can('write:user'):
            raise HTTPException(403, 'Forbidden.')

        user = user_service.get_by_id(id)
        if not user:
            raise HTTPException(404, 'User not found.')

        if data.email and data.email != user.email:
            existing = user_service.get_by_email(data.email)
            if existing and existing.id != user.id:
                raise HTTPException(409, 'Email already in use.')
            user.email = data.email
        if data.first_name:
            user.first_name = data.first_name
        if data.last_name:
            user.last_name = data.last_name
        if data.title is not None:
            user.title = data.title
        if data.profile_picture_url:
            user.profile_picture_url = data.profile_picture_url
        if data.role_id is not None:
            user.role_id = data.role_id
        if data.show_on_page is not None:
            user.show_on_page = data.show_on_page
        if data.password:
            user.password = password_service.hash(data.password)

        user_service.update(user)

        updated = user_service.load_by_id(user.id, with_picture=True)

        return ItemResponse(message='User updated successfully', item=updated)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, 'An unknown error occurred while updating the user.')

@router.delete('/{id}', status_code=204)
def delete_user(id: int, current: RequiresAuth, user_service: RequiresUserService):
    internal_server_error = HTTPException(500, 'An unknown error occurred while deleting the user.')
    try:
        if not current.user.can('delete:user'):
            raise HTTPException(403, 'Forbidden.')
        if user_service.delete(id):
            return 
        raise internal_server_error
    except HTTPException as e:
        raise e
    except:
        raise internal_server_error