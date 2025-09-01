from typing import List

import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.faq.models import FAQ
from wacruit.src.apps.faq.repositories import QuestionRepository
from wacruit.src.apps.faq.schemas import CreateQuestionRequest
from wacruit.src.apps.faq.schemas import UpdateQuestionRequest
from wacruit.src.apps.faq.services import QuestionService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def created_question(db_session: Session) -> FAQ:
    question = FAQ(
        question="개발 경험이 없는데 지원 가능한가요?",
        answer="개발을 처음 접하시는 분들도 물론 준회원(Rookies)으로 지원 가능합니다! \
            와플스튜디오에서 제공하는 세미나를 통해 지식과 협업 경험을 쌓으실 수 있습니다.",
    )
    db_session.add(question)
    db_session.commit()
    return question


@pytest.fixture
def created_questions(db_session: Session) -> List[FAQ]:
    question1 = FAQ(
        question="개발 경험이 없는데 지원 가능한가요?",
        answer="개발을 처음 접하시는 분들도 물론 준회원(Rookies)으로 지원 가능합니다! \
            와플스튜디오에서 제공하는 세미나를 통해 지식과 협업 경험을 쌓으실 수 있습니다.",
    )
    question2 = FAQ(
        question="저학번/고학번/졸업생인데 지원해도 되나요?",
        answer="와플스튜디오는 서울대학교에 재학중이거나 졸업했던 누구나, 나이 제한 없이 가입 가능합니다. \
            다양한 학번으로 구성되어 있어 학번 및 졸업 여부와 상관 없이 지원 가능하니 부담 가지지 말고 지원해주세요!",
    )
    db_session.add_all([question1, question2])
    db_session.commit()
    return [question1, question2]


@pytest.fixture
def create_question_dto() -> CreateQuestionRequest:
    return CreateQuestionRequest(
        question="개발 경험이 없는데 지원 가능한가요?",
        answer="개발을 처음 접하시는 분들도 물론 준회원(Rookies)으로 지원 가능합니다! \
            와플스튜디오에서 제공하는 세미나를 통해 지식과 협업 경험을 쌓으실 수 있습니다.",
    )


@pytest.fixture
def update_question_dto() -> UpdateQuestionRequest:
    return UpdateQuestionRequest(answer="답변 수정")


@pytest.fixture
def question_service(question_repository: QuestionRepository) -> QuestionService:
    return QuestionService(question_repository=question_repository)


@pytest.fixture
def question_repository(db_session: Session) -> QuestionRepository:
    return QuestionRepository(session=db_session, transaction=Transaction(db_session))
