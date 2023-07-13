from datetime import datetime
from typing import Sequence

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.schemas import UserDetailResponse
from wacruit.src.database.base import intpk


class ResumeQuestionDto(BaseModel):
    screening_id: int
    question_num: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ResumeSubmissionDto(BaseModel):
    id: intpk = Field(...)
    user_id: int = Field(...)
    recruiting_id: int = Field(...)
    question_id: int = Field(...)
    answer: str = Field(..., min_length=1, max_length=10000)

    class Config:
        orm_mode = True


class ResumeSubmissionWithUserDto(ResumeSubmissionDto):
    user: UserDetailResponse = Field(...)


class ResumeSubmissionCreateDto(BaseModel):
    user_id: int = Field(...)
    recruiting_id: int = Field(...)
    question_id: int = Field(...)
    answer: str = Field(..., min_length=1, max_length=10000)


class ResumeListingByIdDto(BaseModel):
    recruiting_id: int = Field(...)
