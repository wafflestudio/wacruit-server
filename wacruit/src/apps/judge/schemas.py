from pydantic import BaseModel
from pydantic import Field


class JudgeCreateSubmissionRequest(BaseModel):
    problem_id: int
    source_code: str = Field(..., max_length=10000)
    language_id: int = Field(..., ge=100, le=111)
    stdin: str


class JudgeCreateSubmissionResponse(BaseModel):
    token: str


class JudgeSubmissionStatus(BaseModel):
    id: int
    description: str


class JudgeGetSubmissionResponse(BaseModel):
    stdout: str | None
    stderr: str | None
    compile_output: str | None
    message: str | None
    status: JudgeSubmissionStatus | None
    time: str | None
    memory: int | None
    token: str | None
