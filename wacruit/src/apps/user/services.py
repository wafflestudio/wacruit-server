from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from wacruit.src.apps.user.exceptions import UserAlreadyExistsException
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.schemas import UserCreateResponse
from wacruit.src.apps.user.schemas import UserCreateUpdateRequest
from wacruit.src.apps.user.schemas import UserDetailResponse


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
            first_name=request.first_name,
            last_name=request.last_name,
            department=request.department,
            college=request.college,
            university=request.university,
            phone_number=request.phone_number,
            email=request.email,
        )  # noqa
        try:
            user = self.user_repository.create_user(user)
        except IntegrityError as exc:
            raise UserAlreadyExistsException from exc
        return UserCreateResponse.from_orm(user)

    def list_users(self) -> list[UserDetailResponse]:
        users = self.user_repository.get_users()
        return [UserDetailResponse.from_orm(user) for user in users]
