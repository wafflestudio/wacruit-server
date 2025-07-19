from datetime import date

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field

from wacruit.src.apps.common.schemas import OrmModel


class SponsorCreateRequest(BaseModel):
    name: str
    amount: int = Field(..., gt=0)
    sponsored_date: date
    email: EmailStr | None = None
    phone_number: str | None = None


class SponsorInfoResponse(OrmModel):
    id: int
    name: str
    amount: int = Field(..., gt=0)
    sponsored_date: date
    email: EmailStr | None = None
    phone_number: str | None = None


class SponsorBriefResponse(OrmModel):
    id: int
    name: str


class SponsorUpdateRequest(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = None
    amount: int | None = None
