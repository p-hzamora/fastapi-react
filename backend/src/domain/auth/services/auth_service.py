import uuid
from typing import Optional, Annotated
from fastapi import Request, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ormlambda import ORM

from src.core.constants import ERROR_MESSAGES
from src.core.db import engine

from src.domain.user import Users, UserModel

from .. import log
from ..models import Auth, AuthModel
from ..utils import decode_token, verify_password


bearer_security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    background_tasks: BackgroundTasks,
    auth_token: Annotated[HTTPAuthorizationCredentials, Depends(bearer_security)],
) -> UserModel:
    token = None
    if auth_token is not None:
        token = auth_token.credentials

    if token is None and "token" in request.cookies:
        token = request.cookies["token"]

    if token is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.NOT_AUTHENTICATED)

    # auth by api key
    if token.startswith("sk-"):
        if not request.state.enable_api_key:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.API_KEY_NOT_ALLOWED
            )

        return get_current_user_by_api_key(token)

    # auth by jwt token
    try:
        data = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if data is not None and "id" in data:
        user = Users.get_user_by_id(data["id"])
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.INVALID_TOKEN,
            )
        else:
            # Refresh the user's last active timestamp asynchronously
            # to prevent blocking the request
            if background_tasks:
                background_tasks.add_task(Users.update_user_last_active_by_id, user.id)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )


def get_current_user_by_api_key(api_key: str):
    user = Users.get_user_by_api_key(api_key)

    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.INVALID_TOKEN
        )
    Users.update_user_last_active_by_id(user.id)

    return user


def get_verified_user(user: Annotated[UserModel, Depends(get_current_user)]):
    if user.role not in {"users", "admin"}:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
        )
    return user


def get_admin_user(user: Annotated[UserModel, Depends(get_current_user)]) -> UserModel:
    if user.role != "admin":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=ERROR_MESSAGES.ACCESS_PROHIBITED
        )
    return user


AuthORM = ORM(Auth, engine)


class AuthsTable:
    def insert_new_auth(
        self,
        email: str,
        password: str,
        name: str,
        profile_image_url: str = "/user.png",
        role: str = "pending",
        oauth_sub: Optional[str] = None,
    ) -> Optional[UserModel]:
        log.info("insert_new_auth")

        id = str(uuid.uuid4())

        auth = AuthModel(
            **{
                "id": id,
                "email": email,
                "password": password,
                "active": True,
            }
        )
        result = Auth(**auth.model_dump())
        AuthORM.insert(result)

        user = Users.insert_new_user(
            id, name, email, profile_image_url, role, oauth_sub
        )

        if result and user:
            return user
        return None

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        log.info(f"authenticate_user: {email}")

        try:
            auth = AuthORM.where([Auth.email == email, Auth.active == 1]).first()
            if auth and verify_password(password, auth.password):
                return Users.get_user_by_id(auth.id)
            return None
        except Exception:
            return None

    def authenticate_user_by_api_key(self, api_key: str) -> Optional[UserModel]:
        log.info(f"authenticate_user_by_api_key: {api_key}")
        # if no api_key, return None
        if not api_key:
            return None

        try:
            user = Users.get_user_by_api_key(api_key)
            return user if user else None
        except Exception:
            return False

    def authenticate_user_by_trusted_header(self, email: str) -> Optional[UserModel]:
        log.info(f"authenticate_user_by_trusted_header: {email}")
        try:
            auth = (
                AuthORM.where(lambda x: x.email == email)
                .where(lambda x: x.active is True)
                .select_one()
            )
            if auth:
                user = Users.get_user_by_id(auth.id)
                return user
        except Exception:
            return None

    def update_user_password_by_id(self, id: str, new_password: str) -> bool:
        try:
            result = AuthORM.where(lambda x: x.id == id).update(
                {"password": new_password}
            )
            return True if result == 1 else False
        except Exception:
            return False

    def update_email_by_id(self, id: str, email: str) -> bool:
        try:
            result = AuthORM.where(lambda x: x.id == id).update({"email": email})
            return True if result == 1 else False
        except Exception:
            return False

    def delete_auth_by_id(self, id: str) -> bool:
        try:
            # Delete User
            result = Users.delete_user_by_id(id)

            if result:
                AuthORM.where(lambda x: x.id == id).delete()

                return True
            else:
                return False
        except Exception:
            return False


Auths = AuthsTable()


__all__ = [
    "get_current_user",
    "get_current_user_by_api_key",
    "get_verified_user",
    "get_admin_user",
    "AuthORM",
    "Auths",
]
