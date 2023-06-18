from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.schemas import UserCreateResponse
from wacruit.src.apps.user.schemas import UserCreateUpdateRequest
from wacruit.src.apps.user.schemas import UserDetailResponse
from wacruit.src.database.models import User


class UserService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
    ) -> None:
        self.user_repository = user_repository

    def create_user(self, request: UserCreateUpdateRequest) -> UserCreateResponse:
        if request.sso_id is None:
            raise HTTPException(status_code=400, detail="SSO ID가 필요합니다.")
        user = User(
            sso_id=request.sso_id,
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            positions=request.positions,
            department=request.department,
            college=request.college,
            phone_number=request.phone_number,
            github_id=request.github_id,
            github_email=request.github_email,
            slack_id=request.slack_id,
            slack_email=request.slack_email,
            notion_email=request.notion_email,
            apple_email=request.apple_email,
            introduction=request.introduction,
        )
        try:
            user = self.user_repository.create_user(user)
        except IntegrityError as exc:
            raise UserAlreadyExistsException from exc
        return UserCreateResponse.from_orm(user)

    def list_users(self) -> list[UserDetailResponse]:
        users = self.user_repository.get_users()
        return [UserDetailResponse.from_orm(user) for user in users]
