from datetime import date

from pydantic import BaseModel

from wacruit.src.apps.common.schemas import OrmModel


class SponsorCreateRequest(BaseModel):
    name: str
    amount: int
    sponsored_date: date
    email: str | None = None
    phone_number: str | None = None


class SponsorInfoResponse(OrmModel):
    id: int
    name: str
    amount: int
    sponsored_date: date
    email: str | None = None
    phone_number: str | None = None


class SponsorBriefResponse(OrmModel):
    id: int
    name: str


class SponsorUpdateRequest(BaseModel):
    email: str | None = None
    phone_number: str | None = None
    amount: int | None = None
