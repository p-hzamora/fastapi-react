from typing import Optional
from pydantic import BaseModel as pyBaseModel, ConfigDict
from ormlambda import Column, Table, CHAR, VARCHAR, INT


__all__ = (
    "User",
    "UserSettings",
    "UserModel",
    "UserResponse",
    "UserNameResponse",
    "UserRoleUpdateForm",
    "UserUpdateForm",
)


class User(Table):
    __table_name__ = "user"
    id: Column[CHAR] = Column(CHAR(36), is_primary_key=True)
    name: Column[VARCHAR] = Column(VARCHAR(100))
    email: Column[VARCHAR] = Column(VARCHAR(100))
    role: Column[VARCHAR] = Column(VARCHAR(100))
    profile_image_url: Column[VARCHAR] = Column(VARCHAR(100))

    last_active_at: Column[INT] = Column(INT())  # timestamp in epoch
    updated_at: Column[INT] = Column(INT())  # timestamp in epoch
    created_at: Column[INT] = Column(INT())  # timestamp in epoch

    api_key: Column[VARCHAR] = Column(VARCHAR(40), is_unique=True)
    settings: Column[VARCHAR] = Column(VARCHAR(100))
    info: Column[VARCHAR] = Column(VARCHAR(100))


class UserSettings(pyBaseModel):
    ui: Optional[dict] = {}
    model_config = ConfigDict(extra="allow")


class UserModel(pyBaseModel):
    id: str
    name: str
    email: str
    role: str = "pending"
    profile_image_url: str

    last_active_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch
    created_at: int  # timestamp in epoch

    api_key: Optional[str] = None
    settings: Optional[UserSettings] = None
    info: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################


class UserResponse(pyBaseModel):
    id: str
    name: str
    email: str
    role: str
    profile_image_url: str


class UserNameResponse(UserResponse): ...


class UserRoleUpdateForm(pyBaseModel):
    id: str
    role: str


class UserUpdateForm(pyBaseModel):
    name: str
    email: str
    profile_image_url: str
    password: Optional[str] = None
