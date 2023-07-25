from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.exceptions import UserNotFoundException
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.schemas import UserCreateResponse
from wacruit.src.apps.user.schemas import UserCreateUpdateRequest
from wacruit.src.apps.user.schemas import UserDetailResponse
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest


class UserService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
    ) -> None:
        self.user_repository = user_repository

    def create_user(
        self, sso_id: str, request: UserCreateUpdateRequest
    ) -> UserCreateResponse:
        user = User(
            sso_id=sso_id,
            first_name=request.first_name,
            last_name=request.last_name,
            department=request.department,
            college=request.college,
            university=request.university,
            phone_number=request.phone_number,
            email=request.email,
            github_email=request.email,
            notion_email=request.email,
            slack_email=request.email,
        )  # noqa
        try:
            user = self.user_repository.create_user(user)
        except IntegrityError as exc:
            raise UserAlreadyExistsException from exc
        return UserCreateResponse.from_orm(user)

    def list_users(self) -> list[UserDetailResponse]:
        users = self.user_repository.get_users()
        return [UserDetailResponse.from_orm(user) for user in users]

    def update_invitaion_emails(
        self, user: User, request: UserUpdateInvitationEmailsRequest
    ) -> UserDetailResponse:
        """
        None이 들어오면 기존 이메일을 유지한다.
        """
        user.github_email = request.github_email or user.github_email
        user.notion_email = request.notion_email or user.notion_email
        user.slack_email = request.slack_email or user.slack_email
        updated_user = self.user_repository.update_user(user)
        if updated_user is None:
            raise UserNotFoundException
        return UserDetailResponse.from_orm(user)

    def remove_sensitive_information(self, user_id: int) -> UserDetailResponse:
        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise UserNotFoundException
        user.department = None
        user.college = None
        user.university = None
        user.github_email = None
        user.notion_email = None
        user.slack_email = None
        updated_user = self.user_repository.update_user(user)
        if updated_user is None:
            raise UserNotFoundException
        return UserDetailResponse.from_orm(user)
