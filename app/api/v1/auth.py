import time
import traceback

from fastapi import APIRouter, HTTPException, Request, Response

from app.config.settings import settings
from app.dependencies import (
    RequiresAuthService,
    RequiresClientInfo,
    RequiresCurrentUser,
    RequiresSessionRepository,
    RequiresUserService,
)
from app.schemas.request.forgot_password import ForgotPassword
from app.schemas.request.login_user import LoginUser
from app.schemas.request.reset_password import ResetPassword
from app.schemas.response.auth import TokenResponse
from app.schemas.response.item_response import ItemResponse
from app.schemas.response.list_response import ListResponse
from app.schemas.response.me import Me
from app.schemas.response.session import Session

router = APIRouter(prefix="/auth")


@router.get("/me", response_model=ItemResponse[Me])
def get_current_user(current: RequiresCurrentUser):
    try:
        me = Me.from_current(current)
        return ItemResponse(message="User found", item=me)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(500, "An unknown error occurred while retrieving the current user.")


@router.get("/sessions", response_model=ListResponse[Session])
def get_own_sessions(
    current: RequiresCurrentUser, session_repo: RequiresSessionRepository
):
    try:
        sessions = [
            Session.from_model(s)
            for s in session_repo.get_all_by_uid(current.user.id)
        ]
        return ListResponse(
            message="Session list found",
            items=sessions,
            meta={"count": len(sessions)},
        )
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, "An unknown error occurred while retrieving sessions."
        )


@router.delete("/sessions/{hash}", status_code=204)
def revoke_own_session(
    current: RequiresCurrentUser, hash: str, session_repo: RequiresSessionRepository
):
    try:
        session = session_repo.for_user_by_hash(current.user.id, hash)
        if session is None:
            raise HTTPException(403, "Forbidden.")

        session_repo.delete_by_id(session.id)
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, "An unknown error occurred while revoking the session."
        )


@router.post("/login")
def auth_user(
    data: LoginUser,
    auth_service: RequiresAuthService,
    client_info: RequiresClientInfo,
    response: Response,
):
    try:
        email = data.email.lower()

        result = auth_service.authenticate(
            email,
            data.password,
            client_info.ip_address,
            client_info.user_agent,
            data.remember_me,
        )

        if result is None:
            raise HTTPException(401, "Unauthorized.")

        max_age = auth_service.EXTENDED_AGE if data.remember_me else auth_service.DEFAULT_AGE
        response.set_cookie(
            key="pysessid",
            value=result.pysessid,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=int(max_age.total_seconds()),
            path="/",
        )

        return TokenResponse(
            access_token=result.access_token, expires_in=result.expires_in
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"LOGIN ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(
            500, "An unknown error occurred while logging in."
        )


# ── POST /auth/register ────────────────────────────────────────────────────
# Disabled: this is an admin-only app. Users are created via the admin panel.
#
# @router.post("/register", status_code=201)
# def register_user(
#     data: RegisterUser,
#     auth_service: RequiresAuthService,
#     client_info: RequiresClientInfo,
#     response: Response,
# ):
#     try:
#         result = auth_service.register(
#             data.name,
#             data.email,
#             data.password,
#             client_info.ip_address,
#             client_info.user_agent,
#         )
#
#         if result is None:
#             raise HTTPException(status_code=409, detail="Email already registered.")
#
#         max_age = auth_service.DEFAULT_AGE
#         response.set_cookie(
#             key="pysessid",
#             value=result.pysessid,
#             httponly=True,
#             secure=True,
#             samesite="lax",
#             max_age=int(max_age.total_seconds()),
#             path="/",
#         )
#
#         return TokenResponse(
#             access_token=result.access_token, expires_in=result.expires_in
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         print(f"REGISTER ERROR: {type(e).__name__}: {e}")
#         traceback.print_exc()
#         raise HTTPException(
#             500, "An unknown error occurred while registering."
#         )


@router.post("/refresh")
def refresh_token(
    auth_service: RequiresAuthService,
    request: Request,
):
    try:
        pysessid = request.cookies.get("pysessid")
        if not pysessid:
            raise HTTPException(status_code=401, detail="Unauthorized.")

        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""

        token = auth_service.refresh(pysessid, user_agent, ip_address)
        if token is None:
            raise HTTPException(status_code=401, detail="Unauthorized.")

        return TokenResponse(
            access_token=token, expires_in=settings.jwt_expiry_minutes * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"REFRESH ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(
            500, "An unknown error occurred while refreshing the token."
        )


@router.post("/logout", status_code=204)
def logout(
    auth_service: RequiresAuthService,
    request: Request,
    response: Response,
):
    try:
        pysessid = request.cookies.get("pysessid")
        if pysessid:
            auth_service.revoke(pysessid)

        response.delete_cookie("pysessid", path="/")
    except Exception as e:
        print(f"LOGOUT ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(
            500, "An unknown error occurred while logging out."
        )


@router.post("/password/forgot", status_code=202)
def send_reset_link(
    data: ForgotPassword,
    auth_service: RequiresAuthService,
    user_service: RequiresUserService,
):
    try:
        user = user_service.get_by_email(data.email)

        if user:
            auth_service.create_email_verification(user)
        else:
            time.sleep(1)
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, "An unknown error occurred while sending the reset link."
        )


@router.get("/password/verify", status_code=204)
def verify_token(auth_service: RequiresAuthService, token: str | None = None):
    try:
        unauthorized = HTTPException(401, "Unauthorized.")
        if token is None:
            raise unauthorized
        result = auth_service.verify_token(token)

        if not result:
            raise unauthorized
        return
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, "An unknown error occurred while verifying the token."
        )


@router.post("/password/reset")
def update_user_password(
    data: ResetPassword,
    auth_service: RequiresAuthService,
    token: str | None = None,
):
    try:
        unauthorized = HTTPException(401, "Unauthorized.")
        if token is None:
            raise unauthorized
        result = auth_service.verify_token(token, consume=True)

        if not result:
            raise unauthorized

        auth_service.update_password(result.uid, data.password)
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(
            500, "An unknown error occurred while resetting the password."
        )
