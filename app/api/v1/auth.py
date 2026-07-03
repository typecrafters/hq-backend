from fastapi import APIRouter, HTTPException, Response
from app.dependencies import RequiresAuthService
from app.schemas.request.login_user import LoginUser
from app.schemas.request.forgot_password import ForgotPassword
from app.schemas.request.reset_password import ResetPassword
from app.services.auth_service import AuthService

router = APIRouter(prefix='/auth')


@router.post('/login')
def authenticate_user(data: LoginUser, auth_service: RequiresAuthService, response: Response):
    max_age = AuthService.standard_age

    pysessid = auth_service.auth_user(data.email, data.password, max_age)
    if pysessid is None:
        raise HTTPException(status_code=401, detail='Unauthorized.')

    response.set_cookie(
        key='pysessid',
        value=pysessid,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=int(max_age.total_seconds()),
        path='/'
    )


@router.post('/password/forgot', status_code=201)
def send_password_reset_email(data: ForgotPassword, auth_service: RequiresAuthService):
    auth_service.request_password_reset(data.email)


@router.get('/password/verify')
def verify_reset_token(token: str, auth_service: RequiresAuthService):
    if not auth_service.verify_reset_token(token):
        raise HTTPException(
            status_code=400, detail='Invalid or expired token.')


@router.post('/password/reset')
def reset_password(data: ResetPassword, auth_service: RequiresAuthService):
    if not auth_service.reset_password(data.token, data.password):
        raise HTTPException(
            status_code=400, detail='Invalid or expired token.')
