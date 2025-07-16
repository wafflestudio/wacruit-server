from pydantic import BaseModel


class CreateQuestionRequest(BaseModel):
    question: str
    answer: str


class UpdateQuestionRequest(BaseModel):
    question: str | None = None
    answer: str | None = None


class QuestionResponse(BaseModel):
    id: int
    question: str
    answer: str

    class Config:
        orm_mode = True
