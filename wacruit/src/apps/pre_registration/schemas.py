from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


class CreatePreRegistrationRequest(BaseModel):
    url: str
    generation: str
    is_active: bool


class UpdatePreRegistrationRequest(BaseModel):
    url: str | None = None
    generation: str | None = None
    is_active: bool | None = None


class PreRegistrationResponse(BaseModel):
    id: int
    url: str
    generation: str
    is_active: bool

    class Config:
        orm_mode = True


class CreatePreRegistrationUserRequest(BaseModel):
    name: str = Field(..., max_length=50)
    email: EmailStr
    phone_number: str = Field(..., max_length=30)
    university: str | None = Field(default=None, max_length=50)
    college: str | None = Field(default=None, max_length=50)
    department: str | None = Field(default=None, max_length=50)


class PreRegistrationUserResponse(BaseModel):
    id: int
    pre_registration_id: int
    name: str
    email: str
    phone_number: str
    university: str | None
    college: str | None
    department: str | None

    class Config:
        orm_mode = True


class SendPreRegistrationEmailRequest(BaseModel):
    subject: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    html_content: str | None = None
    active_only: bool = True
    pre_registration_id: int | None = None


class SendPreRegistrationEmailResponse(BaseModel):
    total_count: int
    success_count: int
    failed_count: int
    failed_emails: list[str]
