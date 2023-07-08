from pydantic import BaseModel
from pydantic import Field


class UserCreateUpdateRequest(BaseModel):
    sso_id: str | None = Field(default=None, max_length=50)

    first_name: str = Field(..., max_length=30)
    last_name: str = Field(..., max_length=30)

    phone_number: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=50)

    department: str | None = Field(default=None, max_length=50)
    college: str | None = Field(default=None, max_length=50)
    university: str | None = Field(default=None, max_length=50)


class UserCreateResponse(BaseModel):
    id: int

    first_name: str
    last_name: str

    phone_number: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=50)


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
