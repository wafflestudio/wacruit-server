from typing import List

import pytest

from wacruit.src.apps.faq.exceptions import QuestionNotFoundException
from wacruit.src.apps.faq.models import FAQ
from wacruit.src.apps.faq.schemas import CreateQuestionRequest
from wacruit.src.apps.faq.schemas import UpdateQuestionRequest
from wacruit.src.apps.faq.services import QuestionService


def test_create_question(
    question_service: QuestionService, create_question_dto: CreateQuestionRequest
):
    created_question = question_service.create_question(create_question_dto)
    assert created_question.id is not None
    assert created_question.question == create_question_dto.question
    assert created_question.answer == create_question_dto.answer


def test_update_question(
    question_service: QuestionService,
    created_question: FAQ,
    update_question_dto: UpdateQuestionRequest,
):
    question_id = created_question.id
    updated_question = question_service.update_question(
        question_id, update_question_dto
    )
    assert updated_question.id == question_id
    if update_question_dto.question is not None:
        assert updated_question.question == update_question_dto.question
    if update_question_dto.answer is not None:
        assert updated_question.answer == update_question_dto.answer


def test_get_questions(question_service: QuestionService, created_questions: list[FAQ]):
    questions = question_service.get_questions()
    assert len(questions) == len(created_questions)

    for got, exp in zip(questions, created_questions):
        assert got.id == exp.id
        assert got.question == exp.question
        assert got.answer == exp.answer


def test_delete_question(question_service: QuestionService, created_question: FAQ):
    question_id = created_question.id
    question_service.delete_question(question_id)
    with pytest.raises(QuestionNotFoundException):
        question_service.get_question_by_id(question_id)


def test_delete_question_twice(
    question_service: QuestionService, created_question: FAQ
):
    question_id = created_question.id
    question_service.delete_question(question_id)
    with pytest.raises(QuestionNotFoundException):
        question_service.delete_question(question_id)
