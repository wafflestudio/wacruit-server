from base64 import b64decode

from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from wacruit.src.apps.common.enums import JudgeSubmissionStatus


class JudgeCreateSubmissionRequest(BaseModel):
    source_code: str = Field(..., max_length=100000)
    language_id: int = Field(...)
    stdin: str
    expected_output: str | None
    cpu_time_limit: float = Field(5.0)
    wall_time_limit: float = Field(30.0)
    cpu_extra_time: float = Field(0.0)
    memory_limit: int | None
    stack_limit: int | None
    compiler_options: str | None


class JudgeCreateSubmissionResponse(BaseModel):
    token: str


class JudgeSubmissionStatusModel(BaseModel):
    id: JudgeSubmissionStatus
    description: str

    class Config:
        json_encoders = {JudgeSubmissionStatus: lambda e: e.value}


class JudgeGetSubmissionResponse(BaseModel):
    stdout: str | None
    # stderr: str | None
    # compile_output: str | None
    message: str | None
    status: JudgeSubmissionStatusModel
    time: str | None
    memory: int | None

    class Config:
        json_encoders = {
            JudgeSubmissionStatusModel: lambda v: v.decode() if v is not None else None
        }

    @validator("stdout", pre=True)
    def stdout_validator(cls, v):
        if v is None:
            return None
        return b64decode(v).decode("utf-8")
