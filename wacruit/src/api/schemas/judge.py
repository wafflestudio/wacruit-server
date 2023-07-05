from pydantic import BaseModel
from pydantic import Field


class CreateSubmissionRequest(BaseModel):
    problem_id: int
    source_code: str = Field(..., max_length=10000)
    language_id: int = Field(..., ge=100, le=111)
    stdin: str


class CreateSubmissionResponse(BaseModel):
    token: str


class SubmissionStatus(BaseModel):
    id: int
    description: str


class GetSubmissionResponse(BaseModel):
    stdout: str | None
    stderr: str | None
    compile_output: str | None
    message: str | None
    status: SubmissionStatus | None
    time: str | None
    memory: int | None
    token: str | None


class ErrorResponse(BaseModel):
    error: str
