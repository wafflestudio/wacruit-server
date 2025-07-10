from pydantic import BaseModel

from wacruit.src.apps.common.enums import Position
from wacruit.src.apps.common.schemas import OrmModel


class MemberCreateRequest(BaseModel):
    first_name: str
    last_name: str
    introduction: str | None = None
    department: str
    college: str
    phone_number: str
    github_id: str
    is_active: bool
    generation: str
    position: Position


class MemberInfoResponse(OrmModel):
    first_name: str
    last_name: str
    introduction: str | None = None
    department: str
    college: str
    phone_number: str
    github_id: str
    is_active: bool
    generation: str
    position: Position


class MemberBriefResponse(OrmModel):
    id: int
    first_name: str
    last_name: str
    is_active: bool
    generation: str
    position: Position | None = None


class MemberUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    introduction: str | None = None
    department: str | None = None
    college: str | None = None
    phone_number: str | None = None
    github_id: str | None = None
    is_active: bool | None = None
    generation: str | None = None
    position: Position | None = None
