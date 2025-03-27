from typing import Optional
import uuid
from pydantic import BaseModel as pyBaseModel
from ormlambda import ORM, Table, Column

from src.domain.user.models import Users, UserModel
from src.env import log

from src.core.db import db


####################
# DB MODEL
####################


class Auth(Table):
    __table_name__ = "auth"

    id: Column[str] = Column(str, is_primary_key=True)
    email: Column[str] = Column(str)
    password: Column[str] = Column(str)
    active: Column[int] = Column(int)


AuthORM = ORM(Auth, db)


class AuthModel(pyBaseModel):
    id: str
    email: str
    password: str
    active: bool = True


####################
# Forms
####################


class Token(pyBaseModel):
    token: str
    token_type: str


class ApiKey(pyBaseModel):
    api_key: Optional[str] = None


class UserResponse(pyBaseModel):
    id: str
    email: str
    name: str
    role: str
    profile_image_url: str


class SiginResponse(Token, UserResponse): ...


class SigninForm(pyBaseModel):
    email: str
    password: str


class LdapForm(pyBaseModel):
    user: str
    password: str


class ProfileImageUrlForm(pyBaseModel):
    profile_image_url: str


class UpdateProfileForm(ProfileImageUrlForm):
    name: str


class UpdatePasswordForm(pyBaseModel):
    password: str
    new_password: str


class SignupForm(pyBaseModel):
    name: str
    email: str
    password: str
    profile_image_url: Optional[str] = "/user.png"


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
        else:
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        log.info(f"authenticate_user: {email}")

        try:
            auth = AuthORM.where(
                [
                    Auth.email == email,
                    Auth.active == 1,
                ]
            ).first()
            if auth:
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
    "Auth",
    "AuthModel",
    "Token",
    "ApiKey",
    "UserResponse",
    "SiginResponse",
    "SigninForm",
    "LdapForm",
    "ProfileImageUrlForm",
    "UpdateProfileForm",
    "UpdatePasswordForm",
    "SignupForm",
    "AuthsTable",
    "Auths",
]
