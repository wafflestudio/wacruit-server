from datetime import datetime

from pydantic import BaseModel
from pydantic import Field


class AnnouncementCreateDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=10000)


class AnnouncementDto(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
