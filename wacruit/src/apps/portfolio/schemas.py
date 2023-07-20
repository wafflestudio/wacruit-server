from typing import Any, Literal

from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.judge.schemas import JudgeSubmissionStatusModel


class PresignedUrlResponse(BaseModel):
    object_name: str
    presigned_url: str
