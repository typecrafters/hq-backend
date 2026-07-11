import time

from fastapi import APIRouter, HTTPException, Response

from app.dependencies import RequiresAuth, RequiresAuthService, RequiresClientInfo, RequiresUserService
from app.schemas.request.forgot_password import ForgotPassword
from app.schemas.request.login_user import LoginUser
from app.schemas.request.reset_password import ResetPassword
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.me import Me

router = APIRouter(prefix='/auth')


@router.get('/me', response_model=ItemResponse[Me])
def get_current_user(current: RequiresAuth):
    me = Me.from_current(current)
    return ItemResponse(message='User found', item=me)


@router.post('/login')
def auth_user(data: LoginUser, auth_service: RequiresAuthService, client_info: RequiresClientInfo, response: Response):
    email = data.email.lower()

    session = auth_service.authenticate(
        email,
        data.password,
        client_info.ip_address,
        client_info.user_agent,
        data.remember_me
    )

    max_age = auth_service.EXTENDED_AGE if data.remember_me else auth_service.DEFAULT_AGE

    if session is None:
        raise HTTPException(401, 'Unauthorized.')

    response.set_cookie(
        key='pysessid',
        value=session,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=int(max_age.total_seconds()),
        path='/'
    )


@router.post('/password/forgot', status_code=202)
def send_reset_link(data: ForgotPassword, auth_service: RequiresAuthService, user_service: RequiresUserService):
    user = user_service.get_by_email(data.email)

    if user:
        auth_service.create_email_verification(user)
    else: 
        time.sleep(1)
    return


@router.get('/password/verify', status_code=204)
def verify_token(auth_service: RequiresAuthService, token: str | None = None):
    unauthorized = HTTPException(401, 'Unauthorized.')
    if token is None:
        raise unauthorized
    result = auth_service.verify_token(token)

    if not result:
        raise unauthorized
    return


@router.post('/password/reset')
def update_user_password(data: ResetPassword, auth_service: RequiresAuthService, token: str | None = None):
    unauthorized = HTTPException(401, 'Unauthorized.')
    if token is None:
        raise unauthorized
    result = auth_service.verify_token(token, consume=True)

    if not result:
        raise unauthorized
    
    auth_service.update_password(result.uid, data.password)
