from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.database.models.position import Position
from wacruit.src.database.models.user import User


class UserCreateUpdateRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    first_name: str = Field(..., max_length=20)
    last_name: str = Field(..., max_length=20)
    positions: list[str] = []
    sso_id: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=50)
    college: str | None = Field(default=None, max_length=50)
    phone_number: str | None = Field(default=None, max_length=20)
    github_id: str | None = Field(default=None, max_length=50)
    github_email: str | None = Field(default=None, max_length=50)
    slack_id: str | None = Field(default=None, max_length=50)
    slack_email: str | None = Field(default=None, max_length=50)
    notion_email: str | None = Field(default=None, max_length=50)
    apple_email: str | None = Field(default=None, max_length=50)
    introduction: str | None = Field(default=None, max_length=1000)


class UserCreateResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    image_url: str | None = None

    @staticmethod
    def from_orm(user: User) -> UserCreateResponse:
        return UserCreateResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            image_url=user.image_url,
        )


class PositionDto(BaseModel):
    id: int
    name: str

    @staticmethod
    def from_orm(position: Position) -> PositionDto:
        return PositionDto(
            id=position.id,
            name=position.name,
        )


class UserDetailResponse(BaseModel):
    id: int
    sso_id: str | None
    username: str | None
    first_name: str
    image_url: str | None = None
    last_name: str
    positions: list[PositionDto]
    department: str | None
    college: str | None
    phone_number: str | None
    github_id: str | None
    github_email: str | None
    slack_id: str | None
    slack_email: str | None
    notion_email: str | None
    apple_email: str | None
    introduction: str | None

    @staticmethod
    def from_orm(user: User) -> UserDetailResponse:
        return UserDetailResponse(
            id=user.id,
            sso_id=user.sso_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            image_url=user.image_url,
            positions=[PositionDto.from_orm(pos) for pos in user.positions],
            department=user.department,
            college=user.college,
            phone_number=user.phone_number,
            github_id=user.github_id,
            github_email=user.github_email,
            slack_id=user.slack_id,
            slack_email=user.slack_email,
            notion_email=user.notion_email,
            apple_email=user.apple_email,
            introduction=user.introduction,
        )
