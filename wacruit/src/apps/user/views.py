from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.user.dependencies import AdminUser
from wacruit.src.apps.user.dependencies import CurrentUser
from wacruit.src.apps.user.exceptions import EmailAlreadyExistsException
from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.exceptions import UserNotFoundException
from wacruit.src.apps.user.exceptions import UserPermissionDeniedException
from wacruit.src.apps.user.schemas import UserCreateRequest
from wacruit.src.apps.user.schemas import UserCreateUpdateResponse
from wacruit.src.apps.user.schemas import UserDetailResponse
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.schemas import UserUpdateRequest
from wacruit.src.apps.user.services import UserService

v1_router = APIRouter(prefix="/v1/users", tags=["users"])


@v1_router.patch(
    "", responses=responses_from(UserNotFoundException, EmailAlreadyExistsException)
)
def update_user(
    current_user: CurrentUser,
    request: UserUpdateRequest,
    user_service: Annotated[UserService, Depends()],
) -> UserCreateUpdateResponse:
    return user_service.update_user(user=current_user, request=request)


@v1_router.post("", responses=responses_from(UserAlreadyExistsException))
def create_user(
    request: UserCreateRequest,
    waffle_user_id: Annotated[str, Header()],
    user_service: Annotated[UserService, Depends()],
) -> UserCreateUpdateResponse:
    return user_service.create_user(waffle_user_id, request)


@v1_router.get("", responses=responses_from(UserPermissionDeniedException))
def list_users(
    admin_user: AdminUser,
    user_service: Annotated[UserService, Depends()],
) -> list[UserDetailResponse]:
    return user_service.list_users()


@v1_router.patch(
    "/me/invitation-emails", responses=responses_from(UserNotFoundException)
)
def update_invitation_emails(
    current_user: CurrentUser,
    request: UserUpdateInvitationEmailsRequest,
    user_service: Annotated[UserService, Depends()],
) -> UserDetailResponse:
    return user_service.update_invitaion_emails(user=current_user, request=request)
