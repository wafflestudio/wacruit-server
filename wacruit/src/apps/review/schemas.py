from pydantic import BaseModel

from wacruit.src.apps.common.enums import Position


class ReviewCreateRequest(BaseModel):
    title: str
    content: str
    member_id: int


class ReviewResponse(BaseModel):
    id: int
    title: str
    content: str
    member_id: int
    member_first_name: str
    member_last_name: str
    member_generation: str
    member_position: Position | None
    is_active: bool


class ReviewUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None
    member_id: int | None = None
