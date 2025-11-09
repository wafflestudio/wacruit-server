from typing import Annotated

from fastapi import Depends
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from wacruit.src.apps.auth.services import AuthService
from wacruit.src.apps.user.exceptions import UserPermissionDeniedException
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository

security = HTTPBearer(scheme_name="waffle_token", description="인증을 위한 access token")


def get_current_user(
    waffle_credentials: Annotated[HTTPAuthorizationCredentials, Security(security)],
    auth_service: Annotated[AuthService, Depends()],
) -> User:
    waffle_token = waffle_credentials.credentials
    user_id = auth_service.decode_token(waffle_token)["sub"]
    user = auth_service.get_user_by_id(user_id)
    if user is None:
        raise UserPermissionDeniedException
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_admin_user(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise UserPermissionDeniedException
    return current_user


AdminUser = Annotated[User, Depends(get_admin_user)]
