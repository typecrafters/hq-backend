from fastapi import APIRouter, HTTPException, Response

from app.dependencies import RequiresAuthService
from app.schemas.request.forgot_password import ForgotPassword
from app.schemas.request.login_user import LoginUser

router = APIRouter(prefix='/auth')


@router.post('/login')
def auth_user(data: LoginUser, auth_service: RequiresAuthService, response: Response):
    session = auth_service.authenticate(
        data.email, data.password, data.remember_me)
    max_age = auth_service.EXTENDED_AGE if data.remember_me else auth_service.DEFAULT_AGE

    if session is None:
        raise HTTPException(status_code=401, detail='Unauthorized.')

    response.set_cookie(
        key='pysessid',
        value=session,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=int(max_age.total_seconds()),
        path='/'
    )


@router.post('/password/forgot')
def send_reset_link(data: ForgotPassword, auth_service: RequiresAuthService):
    pass
