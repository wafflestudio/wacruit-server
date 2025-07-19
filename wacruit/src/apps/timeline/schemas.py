from datetime import datetime

from pydantic import BaseModel

from wacruit.src.apps.common.enums import TimelineGroupType
from wacruit.src.apps.common.schemas import OrmModel


class TimelineCategoryCreateUpdateRequest(BaseModel):
    title: str


class TimelineCreateRequest(BaseModel):
    title: str
    group: TimelineGroupType
    category_id: int
    start_date: datetime
    end_date: datetime


class TimelineUpdateRequest(BaseModel):
    title: str | None = None
    group: TimelineGroupType | None = None
    category_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class TimelineCategoryResponse(OrmModel):
    id: int
    title: str


class TimelineResponse(OrmModel):
    id: int
    title: str
    group: TimelineGroupType
    category: TimelineCategoryResponse
    start_date: datetime
    end_date: datetime
