from datetime import datetime
from typing import Sequence

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.schemas import UserDetailResponse
from wacruit.src.database.base import intpk


class ResumeQuestionDto(BaseModel):
    recruiting_id: int
    question_num: int
    content: str
    content_limit: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ResumeSubmissionDto(BaseModel):
    id: int
    user_id: int
    recruiting_id: int
    question_id: int
    created_at: datetime
    updated_at: datetime
    answer: str = Field(..., min_length=1, max_length=10000)

    class Config:
        orm_mode = True


class UserResumeSubmissionDto(ResumeSubmissionDto):
    user: UserDetailResponse


class ResumeSubmissionCreateDto(BaseModel):
    question_id: int
    answer: str = Field(..., min_length=1, max_length=10000)
