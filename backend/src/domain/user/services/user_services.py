import time
from typing import Optional
from ormlambda import ORM

from src.core.db import engine
from src.common.misc import if_error_return
from ..models import UserModel, User


class UsersTable:
    def __init__(self):
        self.model = ORM(User, engine)

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
        self.model.insert(result)
        return user if result else None

    @if_error_return(None)
    def get_user_by_id(self, id: str) -> Optional[UserModel]:
        return self.model.where(lambda x: x.id == id).first(flavour=UserModel)

    @if_error_return(None)
    def get_user_by_api_key(self, api_key: str) -> Optional[UserModel]:
        return self.model.where(lambda x: x.api_key == api_key).first(flavour=UserModel)

    @if_error_return(None)
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.model.where(User.email == email).first(flavour=UserModel)

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
        query = self.model.order(lambda x: x.created_at, order_type="DESC")

        query.offset(skip) if skip else None
        query.limit(limit) if limit else None

        users = query.select()

        return [UserModel.model_validate(user) for user in users]

    # def get_users_by_user_ids(self, user_ids: list[str]) -> list[UserModel]:
    #     with get_db() as db:
    #         users = db.query(User).filter(User.id.in_(user_ids)).all()
    #         return [UserModel.model_validate(user) for user in users]

    def get_num_users(self) -> Optional[int]:
        return self.model.count(execute=True)

    @if_error_return(None)
    def get_first_user(self) -> UserModel:
        return self.model.order(lambda x: x.created_at, order_type="DESC").first(
            flavour=UserModel
        )

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

    @if_error_return(None)
    def update_user_role_by_id(self, id: str, role: str) -> Optional[UserModel]:
        self.model.where(lambda x: x.id == id).update({"role": role})
        user = self.model.where(lambda x: x.id == id).first()
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

    @if_error_return(None)
    def update_user_last_active_by_id(self, id: str) -> Optional[UserModel]:
        self.model.where(lambda x: x.id == id).update(
            {User.last_active_at: int(time.time())}
        )
        user = self.model.where(User.id == id).first()
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

    @if_error_return(False)
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

    @if_error_return(False)
    def update_user_api_key_by_id(self, id: str, api_key: str) -> bool:
        self.model.where(lambda x: x.id == id).update({User.api_key: api_key})
        return True

    @if_error_return(None)
    def get_user_api_key_by_id(self, id: str) -> Optional[str]:
        return self.model.where(User.id == id).first().api_key

    # def get_valid_user_ids(self, user_ids: list[str]) -> list[str]:
    #     with get_db() as db:
    #         users = db.query(User).filter(User.id.in_(user_ids)).all()
    #         return [user.id for user in users]


Users = UsersTable()
