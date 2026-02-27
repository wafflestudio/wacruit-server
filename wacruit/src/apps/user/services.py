from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError

from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.user.exceptions import EmailAlreadyExistsException
from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.exceptions import UserNotFoundException
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.schemas import SignupCheckResponse
from wacruit.src.apps.user.schemas import UserCreateRequest
from wacruit.src.apps.user.schemas import UserCreateUpdateResponse
from wacruit.src.apps.user.schemas import UserDetailResponse
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.schemas import UserUpdateRequest


class UserService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
    ) -> None:
        self.user_repository = user_repository

    def check_signup(self, sso_id: str) -> SignupCheckResponse:
        return SignupCheckResponse(
            signup=self.user_repository.check_signup_by_sso_id(sso_id)
        )

    def create_user(self, request: UserCreateRequest) -> UserCreateUpdateResponse:
        if self.user_repository.get_user_by_email(request.email):
            raise EmailAlreadyExistsException
        user = User(
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
            password=PasswordService.hash_password(request.password),
        )  # noqa
        try:
            user = self.user_repository.create_user(user)
        except IntegrityError as exc:
            raise UserAlreadyExistsException from exc
        return UserCreateUpdateResponse.from_orm(user)

    def update_user(
        self, user: User, request: UserUpdateRequest
    ) -> UserCreateUpdateResponse:
        for key, value in request.dict(exclude_none=True).items():
            setattr(user, key, value)
        try:
            updated_user = self.user_repository.update_user(user)
            if updated_user is None:
                raise UserNotFoundException
            return UserCreateUpdateResponse.from_orm(user)
        except IntegrityError as exc:
            raise EmailAlreadyExistsException from exc

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
