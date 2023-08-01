from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

from wacruit.src.apps.common.schemas import OrmModel


class UserCreateRequest(BaseModel):
    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)

    phone_number: str = Field(max_length=30)
    email: EmailStr

    department: str | None = Field(default=None, max_length=50)
    college: str | None = Field(default=None, max_length=50)
    university: str | None = Field(default=None, max_length=50)


class UserUpdateRequest(BaseModel):
    first_name: str | None = Field(max_length=30)
    last_name: str | None = Field(max_length=30)

    phone_number: str | None = Field(max_length=30)
    email: EmailStr | None

    department: str | None = Field(max_length=50)
    college: str | None = Field(max_length=50)
    university: str | None = Field(max_length=50)


class UserCreateUpdateResponse(OrmModel):
    id: int

    first_name: str
    last_name: str

    phone_number: str | None
    email: str | None

    department: str | None
    college: str | None
    university: str | None


class UserUpdateInvitationEmailsRequest(BaseModel):
    github_email: EmailStr | None = None
    slack_email: EmailStr | None = None
    notion_email: EmailStr | None = None


class UserDetailResponse(BaseModel):
    id: int
    sso_id: str | None

    first_name: str
    last_name: str

    phone_number: str | None
    email: str | None

    department: str | None
    college: str | None
    university: str | None

    github_email: str | None
    slack_email: str | None
    notion_email: str | None

    class Config:
        orm_mode = True
