from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import SeminarType


class CreateSeminarRequest(BaseModel):
    seminar_type: SeminarType
    curriculum_info: str
    prerequisite_info: str
    is_active: bool


class UpdateSeminarRequest(BaseModel):
    seminar_type: SeminarType | None = None
    curriculum_info: str | None = None
    prerequisite_info: str | None = None
    is_active: bool | None = None


class SeminarResponse(BaseModel):
    id: int
    seminar_type: SeminarType
    curriculum_info: str
    prerequisite_info: str

    class Config:
        orm_mode = True


class SeminarListResponse(BaseModel):
    items: list[SeminarResponse]
