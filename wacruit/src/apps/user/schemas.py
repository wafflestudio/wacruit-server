from email_validator import EmailNotValidError
from email_validator import validate_email
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator


class UserCreateUpdateRequest(BaseModel):
    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)

    phone_number: str = Field(max_length=30)
    email: str = Field(max_length=50)

    department: str | None = Field(default=None, max_length=50)
    college: str | None = Field(default=None, max_length=50)
    university: str | None = Field(default=None, max_length=50)

    @validator("email")
    def validate_email(cls, v):
        validate_email(v, check_deliverability=True)
        return v


class UserCreateResponse(BaseModel):
    id: int

    first_name: str
    last_name: str

    phone_number: str | None
    email: str | None

    class Config:
        orm_mode = True


class UserUpdateInvitationEmailsRequest(BaseModel):
    github_email: str | None = Field(default=None, max_length=200)
    slack_email: str | None = Field(default=None, max_length=200)
    notion_email: str | None = Field(default=None, max_length=200)

    @validator("github_email", "slack_email", "notion_email")
    def validate_email(cls, v):
        if v is not None:
            validate_email(v, check_deliverability=True)
        return v


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
