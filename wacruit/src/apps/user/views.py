from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header

from wacruit.src.apps.user.dependencies import AdminUser
from wacruit.src.apps.user.dependencies import CurrentUser
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.schemas import UserCreateUpdateRequest
from wacruit.src.apps.user.schemas import UserDetailResponse
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.services import UserService

v1_router = APIRouter(prefix="/v1/users", tags=["users"])


@v1_router.post("")
def create_user(
    request: UserCreateUpdateRequest,
    waffle_user_id: Annotated[str, Header()],
    user_service: Annotated[UserService, Depends()],
):
    return user_service.create_user(waffle_user_id, request)


@v1_router.get("")
def list_users(
    admin_user: AdminUser,
    user_service: Annotated[UserService, Depends()],
):
    return user_service.list_users()


@v1_router.patch("/me/invitation-emails")
def update_invitation_emails(
    current_user: CurrentUser,
    request: UserUpdateInvitationEmailsRequest,
    user_service: Annotated[UserService, Depends()],
) -> UserDetailResponse:
    return user_service.update_invitaion_emails(user=current_user, request=request)
