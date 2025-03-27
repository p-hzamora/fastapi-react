import time
from typing import Callable, Optional
from pydantic import BaseModel as pyBaseModel, ConfigDict
from ormlambda import ORM, Column, Table
from src.core.db import db


class User(Table):
    __table_name__ = "user"
    id: Column[str] = Column(str, is_primary_key=True)
    name: Column[str]
    email: Column[str]
    role: Column[str]
    profile_image_url: Column[str]

    last_active_at: Column[int]  # timestamp in epoch
    updated_at: Column[int]  # timestamp in epoch
    created_at: Column[int]  # timestamp in epoch

    api_key: Column[str] = Column(str, is_unique=True)
    settings: Column[str]
    info: Column[str]


UserORM = ORM(User, db)


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


def return_if_error[TError](return_if_error: TError):
    def decorator[T, **P](f: Callable[P, T]) -> Callable[P, T]:
        def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return f(*args, **kwargs)
            except Exception:
                return return_if_error

        return inner

    return decorator


class UsersTable:
    def insert_new_user(
        self,
        id: str,
        name: str,
        email: str,
        profile_image_url: str = "/user.png",
        role: str = "pending",
        oauth_sub: Optional[str] = None,
    ) -> Optional[UserModel]:
        user = UserModel(
            **{
                "id": id,
                "name": name,
                "email": email,
                "role": role,
                "profile_image_url": profile_image_url,
                "last_active_at": int(time.time()),
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
                "oauth_sub": oauth_sub,
            }
        )
        result = User(**user.model_dump())
        UserORM.insert(result)
        return user if result else None

    @return_if_error(None)
    def get_user_by_id(self, id: str) -> Optional[UserModel]:
        user = UserORM.where(User.id == id).first()
        return UserModel.model_validate(user)

    @return_if_error(None)
    def get_user_by_api_key(self, api_key: str) -> Optional[UserModel]:
        user = UserORM.where(User.api_key == api_key).first()
        return UserModel.model_validate(user)

    @return_if_error(None)
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        user = UserORM.where(User.email == email).first()
        return UserModel.model_validate(user)

    # def get_user_by_oauth_sub(self, sub: str) -> Optional[UserModel]:
    #     try:
    #         with get_db() as db:
    #             user = db.query(User).filter_by(oauth_sub=sub).first()
    #             return UserModel.model_validate(user)
    #     except Exception:
    #         return None

    def get_users(
        self, skip: Optional[int] = None, limit: Optional[int] = None
    ) -> list[UserModel]:
        query = UserORM.order(lambda x: x.created_at, order_type="DESC")

        if skip:
            query.offset(skip)
        if limit:
            query.limit(limit)

        users = query.select()

        return [UserModel.model_validate(user) for user in users]

    # def get_users_by_user_ids(self, user_ids: list[str]) -> list[UserModel]:
    #     with get_db() as db:
    #         users = db.query(User).filter(User.id.in_(user_ids)).all()
    #         return [UserModel.model_validate(user) for user in users]

    def get_num_users(self) -> Optional[int]:
        return UserORM.count(execute=True)

    @return_if_error(None)
    def get_first_user(self) -> UserModel:
        user = UserORM.order(lambda x: x.created_at, order_type="DESC").first()
        return UserModel.model_validate(user)

    # def get_user_webhook_url_by_id(self, id: str) -> Optional[str]:
    #     try:
    #         with get_db() as db:
    #             user = db.query(User).filter_by(id=id).first()

    #             if user.settings is None:
    #                 return None
    #             else:
    #                 return (
    #                     user.settings.get("ui", {})
    #                     .get("notifications", {})
    #                     .get("webhook_url", None)
    #                 )
    #     except Exception:
    #         return None

    @return_if_error(None)
    def update_user_role_by_id(self, id: str, role: str) -> Optional[UserModel]:
        UserORM.where(lambda x: x.id == id).update({"role": role})
        user = UserORM.where(lambda x: x.id == id).first()
        return UserModel.model_validate(user)

    # def update_user_profile_image_url_by_id(
    #     self, id: str, profile_image_url: str
    # ) -> Optional[UserModel]:
    #     try:
    #         with get_db() as db:
    #             db.query(User).filter_by(id=id).update(
    #                 {"profile_image_url": profile_image_url}
    #             )
    #             db.commit()

    #             user = db.query(User).filter_by(id=id).first()
    #             return UserModel.model_validate(user)
    #     except Exception:
    #         return None

    @return_if_error(None)
    def update_user_last_active_by_id(self, id: str) -> Optional[UserModel]:
        UserORM.where(lambda x: x.id == id).update(
            {User.last_active_at: int(time.time())}
        )
        user = UserORM.where(User.id == id).first()
        return UserModel.model_validate(user)

    # def update_user_oauth_sub_by_id(
    #     self, id: str, oauth_sub: str
    # ) -> Optional[UserModel]:
    #     try:
    #         with get_db() as db:
    #             db.query(User).filter_by(id=id).update({"oauth_sub": oauth_sub})
    #             db.commit()

    #             user = db.query(User).filter_by(id=id).first()
    #             return UserModel.model_validate(user)
    #     except Exception:
    #         return None

    # def update_user_by_id(self, id: str, updated: dict) -> Optional[UserModel]:
    #     try:
    #         with get_db() as db:
    #             db.query(User).filter_by(id=id).update(updated)
    #             db.commit()

    #             user = db.query(User).filter_by(id=id).first()
    #             return UserModel.model_validate(user)
    #             # return UserModel(**user.dict())
    #     except Exception:
    #         return None

    @return_if_error(False)
    def delete_user_by_id(self, id: str) -> bool:
        # # Remove User from Groups
        # Groups.remove_user_from_all_groups(id)

        # # Delete User Chats
        # result = Chats.delete_chats_by_user_id(id)
        # if result:
        #     with get_db() as db:
        #         # Delete User
        #         db.query(User).filter_by(id=id).delete()
        #         db.commit()

        #     return True
        # return False
        return True

    @return_if_error(False)
    def update_user_api_key_by_id(self, id: str, api_key: str) -> bool:
        UserORM.where(lambda x: x.id == id).update({User.api_key: api_key})
        return True

    @return_if_error(None)
    def get_user_api_key_by_id(self, id: str) -> Optional[str]:
        return UserORM.where(lambda x: x.id == id).first().api_key

    # def get_valid_user_ids(self, user_ids: list[str]) -> list[str]:
    #     with get_db() as db:
    #         users = db.query(User).filter(User.id.in_(user_ids)).all()
    #         return [user.id for user in users]


Users = UsersTable()
