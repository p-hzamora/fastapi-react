from typing import Optional
from pydantic import BaseModel
from ormlambda import Table, Column, VARCHAR,INT, CHAR


####################
# DB MODEL
####################


class Auth(Table):
    __table_name__ = "auth"

    id: Column[CHAR] = Column(CHAR(36), is_primary_key=True)
    email: Column[VARCHAR] = Column(VARCHAR(255))
    password: Column[VARCHAR] = Column(VARCHAR(255))
    active: Column[INT] = Column(INT())


class AuthModel(BaseModel):
    id: str
    email: str
    password: str
    active: bool = True


####################
# Forms
####################


class Token(BaseModel):
    token: str
    token_type: str


class ApiKey(BaseModel):
    api_key: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    profile_image_url: str


class SiginResponse(Token, UserResponse): ...


class SigninForm(BaseModel):
    email: str
    password: str


class LdapForm(BaseModel):
    user: str
    password: str


class ProfileImageUrlForm(BaseModel):
    profile_image_url: str


class UpdateProfileForm(ProfileImageUrlForm):
    name: str


class UpdatePasswordForm(BaseModel):
    password: str
    new_password: str


class SignupForm(BaseModel):
    name: str
    email: str
    password: str
    profile_image_url: Optional[str] = "/user.png"
