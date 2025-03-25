import logging
from typing import Optional
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.env import SRC_LOG_LEVELS
from backend.domain.user.models.user import UserModel, Users, UserRoleUpdateForm
from backend.constants import ERROR_MESSAGES

from backend.domain.auth.utils import (
    get_admin_user,
    get_verified_user,
)

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

router = APIRouter()


############################
# GetUsers
############################


@router.get("/", response_model=list[UserModel], dependencies=[Depends(get_admin_user)])
async def get_users(
    skip: Optional[int] = None,
    limit: Optional[int] = None,
):
    return Users.get_users(skip, limit)


############################
# UpdateUserRole
############################


@router.post("/update/role", response_model=Optional[UserModel])
async def update_user_role(
    form_data: UserRoleUpdateForm, user: Annotated[UserModel, Depends(get_admin_user)]
):
    if user.id != form_data.id and form_data.id != Users.get_first_user().id:
        return Users.update_user_role_by_id(form_data.id, form_data.role)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail=ERROR_MESSAGES.ACTION_PROHIBITED
    )


############################
# GetUserById
############################


def get_activate_status_by_user_id(user_id: str) -> bool:
    return True


class UserResponse(BaseModel):
    name: str
    profile_image_url: str
    active: Optional[bool] = None


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, user=Depends(get_verified_user)):
    user = Users.get_user_by_id(user_id)
    if user:
        return UserResponse(
            **{
                "name": user.name,
                "profile_image_url": user.profile_image_url,
                "active": get_activate_status_by_user_id(user_id),
            }
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.USER_NOT_FOUND
    )
