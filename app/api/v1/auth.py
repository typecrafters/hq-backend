import time
from fastapi import APIRouter, HTTPException, Response
from app.dependencies import RequiresAuth, RequiresAuthService, RequiresClientInfo, RequiresSessionRepository, RequiresUserService
from app.schemas.response.session import Session
from app.schemas.request.forgot_password import ForgotPassword
from app.schemas.request.login_user import LoginUser
from app.schemas.request.reset_password import ResetPassword
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.list_response import ListResponse
from app.schemas.response.me import Me

router = APIRouter(prefix='/auth') 


@router.get('/me', response_model=ItemResponse[Me])
def get_current_user(current: RequiresAuth):
    try:
        me = Me.from_current(current)
        return ItemResponse(message='User found', item=me)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while retrieving the current user.')

@router.get('/sessions', response_model=ListResponse[Session])
def get_own_sessions(current: RequiresAuth, session_repo: RequiresSessionRepository):
    try:
        sessions = [Session.from_model(s) for s in session_repo.get_all_by_uid(current.user.id)]
        return ListResponse(message='Session list found', items=sessions, meta={ 'count': len(sessions) })
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while retrieving sessions.')

@router.delete('/sessions/{hash}', status_code=204)
def revoke_own_session(current: RequiresAuth, hash: str, session_repo: RequiresSessionRepository):
    try:
        session = session_repo.for_user_by_hash(current.user.id, hash)
        if session is None:
            raise HTTPException(403, 'Forbidden.')

        session_repo.delete_by_id(session.id)
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while revoking the session.')

@router.post('/login')
def auth_user(data: LoginUser, auth_service: RequiresAuthService, client_info: RequiresClientInfo, response: Response):
    try:
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
            httponly=False,
            secure=False,
            samesite='lax',
            max_age=int(max_age.total_seconds()),
            path='/'
        )

        return {"session_id": session}
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while logging in.')


@router.post('/password/forgot', status_code=202)
def send_reset_link(data: ForgotPassword, auth_service: RequiresAuthService, user_service: RequiresUserService):
    try:
        user = user_service.get_by_email(data.email)

        if user:
            auth_service.create_pw_verification_token(user)
        else:
            time.sleep(1)
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while sending the reset link.')


@router.get('/password/verify', status_code=204)
def verify_token(auth_service: RequiresAuthService, token: str | None = None):
    try:
        unauthorized = HTTPException(401, 'Unauthorized.')
        if token is None:
            raise unauthorized
        result = auth_service.verify_token(token)

        if not result:
            raise unauthorized
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while verifying the token.')


@router.get('/email/verify', status_code=204)
def verify_email_token(auth_service: RequiresAuthService, token: str | None = None):
    try:
        unauthorized = HTTPException(401, 'Unauthorized.')
        if token is None:
            raise unauthorized
        result = auth_service.verify_token(token, consume=True)

        if not result:
            raise unauthorized
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while verifying the token.')


@router.post('/password/reset')
def update_user_password(data: ResetPassword, auth_service: RequiresAuthService, token: str | None = None):
    try:
        unauthorized = HTTPException(401, 'Unauthorized.')
        if token is None:
            raise unauthorized
        result = auth_service.verify_token(token, consume=True)

        if not result:
            raise unauthorized

        auth_service.update_password(result.uid, data.password)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, 'An unknown error occurred while resetting the password.')