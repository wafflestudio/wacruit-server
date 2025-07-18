from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.faq.exceptions import QuestionNowFoundException
from wacruit.src.apps.faq.models import FAQ
from wacruit.src.apps.faq.repositories import QuestionRepository
from wacruit.src.apps.faq.schemas import UpdateQuestionRequest


class QuestionService:
    def __init__(self, question_repository: Annotated[QuestionRepository, Depends()]):
        self.question_repository = question_repository

    def get_question_by_id(self, questions_id: int) -> FAQ:
        question = self.question_repository.get_question_by_id(questions_id)
        if question is None:
            raise QuestionNowFoundException
        return question

    def create_question(self, question: FAQ) -> FAQ:
        return self.question_repository.create_questions(question)

    def get_questions(self) -> list[FAQ]:
        questions = self.question_repository.get_questions()
        return questions

    def update_question(self, questions_id: int, req: UpdateQuestionRequest) -> FAQ:
        question = self.get_question_by_id(questions_id)
        for key, value in req.dict(exclude_none=True).items():
            setattr(question, key, value)
        return self.question_repository.update_question(question)

    def delete_question(self, questions_id: int) -> None:
        self.get_question_by_id(questions_id)
        self.question_repository.delete_question(questions_id)
