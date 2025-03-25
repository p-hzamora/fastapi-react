import time
from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from pydantic import BaseModel
import logging
import datetime

from backend.env import (
    SRC_LOG_LEVELS,
    BACKEND_AUTH,
    BACKEND_AUTH_TRUSTED_EMAIL_HEADER,
    BACKEND_AUTH_TRUSTED_NAME_HEADER,
    BACKEND_SESSION_COOKIE_SAME_SITE,
    BACKEND_SESSION_COOKIE_SECURE,
)
from backend.domain.auth.utils import (
    create_api_key,
    create_token,
    # get_admin_user,
    # get_verified_user,
    get_current_user,
    get_password_hash,
)
from backend.constants import ERROR_MESSAGES
from backend.common.misc import validate_email_format
from backend.domain.auth.models.auth import (
    ApiKey,
    Token,
    SigninForm,
    SignupForm,
    Auths,
)
from backend.common.misc import parse_duration
from backend.domain.user.models.user import Users, UserModel, UserResponse


class RouterResponse(BaseModel):
    username: str
    password: str


router = APIRouter()


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])


############################
# GetSessionUser
############################


class SessionUserResponse(Token, UserResponse):
    expires_at: Optional[int] = None
    permissions: Optional[dict] = None


@router.post("/api_key", response_model=ApiKey)
async def generate_api_key(user: Annotated[UserModel, Depends(get_current_user)]):
    api_key = create_api_key()
    success = Users.update_user_api_key_by_id(user.id, api_key)

    if success:
        return {"api_key": api_key}
    raise HTTPException(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=ERROR_MESSAGES.CREATE_API_KEY_ERROR,
    )


@router.delete("/api_key", response_model=bool)
async def delete_api_key(user: Annotated[UserModel, Depends(get_current_user)]):
    return Users.update_user_api_key_by_id(user.id, None)


@router.get("/api_key", response_model=ApiKey)
async def get_api_key(user: Annotated[UserModel, Depends(get_current_user)]):
    api_key = Users.get_user_api_key_by_id(user.id)
    if api_key:
        return {
            "api_key": api_key,
        }
    raise HTTPException(
        status.HTTP_404_NOT_FOUND, detail=ERROR_MESSAGES.API_KEY_NOT_FOUND
    )


############################
# SignIn
############################


@router.post("/signin", response_model=SessionUserResponse)
async def signin(request: Request, response: Response, form_data: SigninForm):
    if BACKEND_AUTH_TRUSTED_EMAIL_HEADER:
        if BACKEND_AUTH_TRUSTED_EMAIL_HEADER not in request.headers:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_TRUSTED_HEADER,
            )
        trusted_email = request.headers[BACKEND_AUTH_TRUSTED_EMAIL_HEADER].lower()
        trusted_name = trusted_email
        if BACKEND_AUTH_TRUSTED_NAME_HEADER:
            trusted_name = request.headers.get(
                BACKEND_AUTH_TRUSTED_NAME_HEADER, trusted_email
            )

        if not Users.get_user_by_email(trusted_name.lower()):
            await signup(request)

    elif BACKEND_AUTH is False:
        admin_email = "admin@localhost"
        admin_password = "admin"
        if Users.get_user_by_email(admin_email):
            user = Auths.authenticate_user(admin_email, admin_password)
        else:
            if Users.get_num_users() != 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.EXISTING_USERS,
                )
            await signup(
                request,
                response,
                SignupForm(email=admin_email, password=admin_password, name="User"),
            )
            user = Auths.authenticate_user(admin_email, admin_password)
    else:
        user = Auths.authenticate_user(form_data.email.lower(), form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.INVALID_CRED
        )

    expires_delta = parse_duration(request.app.state.config.JWT_EXPIRES_IN)
    expires_at = None
    if expires_delta:
        expires_at = int(time.time()) + int(expires_delta.total_seconds())

    token = create_token(data={"id": user.id}, expires_delta=expires_delta)
    datetime_expires_at = (
        datetime.datetime.fromtimestamp(expires_at, datetime.timezone.utc)
        if expires_at
        else None
    )

    # Set the cookie token
    response.set_cookie(
        key="token",
        value=token,
        expires=datetime_expires_at,
        httponly=True,  # Ensures the cookie is not accessible via JavaScript
        samesite=BACKEND_SESSION_COOKIE_SAME_SITE,
        secure=BACKEND_SESSION_COOKIE_SECURE,
    )

    # user_permissions= get_permissions(
    #     user.id, request.app.state.config.USER_PERMISSIONS
    # )

    return {
        "token": token,
        "token_type": "Bearer",
        "expires_at": expires_at,
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "profile_image_url": user.profile_image_url,
        # "permissions": user_permissions,
    }


############################
# SignUp
############################
@router.post("/signup", response_model=SessionUserResponse)
async def signup(request: Request, response: Response, form_data: SignupForm):
    if BACKEND_AUTH:
        if (
            not request.app.state.config.ENABLE_SIGNUP
            or not request.app.state.config.ENABLE_LOGIN_FORM
        ):
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

    else:
        if Users.get_num_users() != 0:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
            )

    if not validate_email_format(form_data.email.lower()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.INVALID_EMAIL_FORMAT
        )

    if Users.get_user_by_email(form_data.email.lower()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.EMAIL_TAKEN
        )

    try:
        num_users: int = Users.get_num_users()
        role = "admin" if num_users == 0 else request.app.state.config.DEFAULT_USER_ROLE

        if num_users == 0:
            request.app.state.config.ENABLE_SIGNUP = False

        hashed = get_password_hash(form_data.password)
        user = Auths.insert_new_auth(
            form_data.email.lower(),
            hashed,
            form_data.name,
            form_data.profile_image_url,
            role,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR_MESSAGES.CREATE_USER_ERROR,
            )

        expires_delta = parse_duration(request.app.state.config.JWT_EXPIRES_IN)
        expires_at = None
        if expires_delta:
            expires_at = int(time.time()) + int(expires_delta.total_seconds())

        token = create_token(data={"id": user.id}, expires_delta=expires_delta)
        datetime_expires_at = (
            datetime.datetime.fromtimestamp(expires_at, datetime.timezone.utc)
            if expires_at
            else None
        )

        # Set the cookie token
        response.set_cookie(
            key="token",
            value=token,
            expires=datetime_expires_at,
            httponly=True,  # Ensures the cookie is not accessible via JavaScript
            samesite=BACKEND_SESSION_COOKIE_SAME_SITE,
            secure=BACKEND_SESSION_COOKIE_SECURE,
        )

        if request.app.state.config.BACKEND_URL:
            ...

        # user_permissions = get_permissions(
        #     user.id, request.app.state.config.USER_PERMISSIONS
        # )

        return {
            "token": token,
            "token_type": "Bearer",
            "expires_at": expires_at,
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "profile_image_url": user.profile_image_url,
            # "permissions": user_permissions,
        }

    except Exception as err:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ERROR_MESSAGES.DEFAULT(err)
        )
