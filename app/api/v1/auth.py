import traceback
from fastapi import APIRouter, HTTPException, Request, Response

from app.config.settings import settings
from app.dependencies import RequiresAuthService
from app.schemas.request.login_user import LoginUser
from app.schemas.request.register_user import RegisterUser
from app.schemas.response.auth import TokenResponse

router = APIRouter(prefix="/auth")


@router.post("/login")
def auth_user(
    data: LoginUser,
    auth_service: RequiresAuthService,
    response: Response,
    request: Request,
):
    try:
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""
        result = auth_service.authenticate(data.email, data.password, data.remember_me, user_agent, ip_address)

        if result is None:
            raise HTTPException(status_code=401, detail="Unauthorized.")

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

        return TokenResponse(access_token=result.access_token, expires_in=result.expires_in)
    except Exception as e:
        print(f"LOGIN ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise


@router.post("/register", status_code=201)
def register_user(
    data: RegisterUser,
    auth_service: RequiresAuthService,
    response: Response,
    request: Request,
):
    try:
        user_agent = request.headers.get("user-agent", "")
        ip_address = request.client.host if request.client else ""
        result = auth_service.register(data.name, data.email, data.password, user_agent, ip_address)

        if result is None:
            raise HTTPException(status_code=409, detail="Email already registered.")

        max_age = auth_service.DEFAULT_AGE
        response.set_cookie(
            key="pysessid",
            value=result.pysessid,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=int(max_age.total_seconds()),
            path="/",
        )

        return TokenResponse(access_token=result.access_token, expires_in=result.expires_in)
    except HTTPException:
        raise
    except Exception as e:
        print(f"REGISTER ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise


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

        return TokenResponse(access_token=token, expires_in=settings.jwt_expiry_minutes * 60)
    except Exception as e:
        print(f"REFRESH ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise


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
        raise
