from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.faq.models import FAQ
from wacruit.src.apps.faq.schemas import CreateQuestionRequest
from wacruit.src.apps.faq.schemas import QuestionResponse
from wacruit.src.apps.faq.schemas import UpdateQuestionRequest
from wacruit.src.apps.faq.services import QuestionService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/questions", tags=["questions"])


@v3_router.get(path="", status_code=HTTPStatus.OK)
def get_questions(
    question_service: Annotated[QuestionService, Depends()]
) -> ListResponse[QuestionResponse]:
    res = question_service.get_questions()
    items = []

    for q in res:
        items.append(QuestionResponse.from_orm(q))

    return ListResponse(items=items)


@v3_router.post(path="", status_code=HTTPStatus.CREATED)
def create_question(
    admin_user: AdminUser,
    request: CreateQuestionRequest,
    question_service: Annotated[QuestionService, Depends()],
) -> QuestionResponse:
    res = question_service.create_question(request)

    return QuestionResponse.from_orm(res)


@v3_router.patch(path="/{questions_id}", status_code=HTTPStatus.OK)
def update_question(
    admin_user: AdminUser,
    questions_id: int,
    request: UpdateQuestionRequest,
    question_service: Annotated[QuestionService, Depends()],
) -> QuestionResponse:
    res = question_service.update_question(questions_id, request)

    return QuestionResponse.from_orm(res)


@v3_router.delete(path="/{questions_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_question(
    admin_user: AdminUser,
    questions_id: int,
    question_service: Annotated[QuestionService, Depends()],
) -> None:
    question_service.delete_question(questions_id)
