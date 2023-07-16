from pydantic import BaseModel
from pydantic import Field

from wacruit.src.apps.common.enums import JudgeSubmissionStatus


class JudgeCreateSubmissionRequest(BaseModel):
    problem_id: int
    source_code: str = Field(..., max_length=10000)
    language_id: int = Field(..., ge=100, le=111)
    stdin: str
    expected_output: str
    cpu_time_limit: float


class JudgeCreateSubmissionResponse(BaseModel):
    token: str


class JudgeSubmissionStatusModel(BaseModel):
    id: JudgeSubmissionStatus
    description: str


class JudgeGetSubmissionResponse(BaseModel):
    stdout: str | None
    stderr: str | None
    compile_output: str | None
    message: str | None
    status: JudgeSubmissionStatusModel
    time: float | None
    memory: int | None
