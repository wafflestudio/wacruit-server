from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.repositories import ResumeRepository
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.services import UserService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(
        sso_id="abcdef123",
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="example@email.com",
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def recruiting(db_session: Session):
    recruiting = Recruiting(
        name="Example Recruiting",
        is_active=True,
        from_date=datetime.utcnow(),
        to_date=datetime.utcnow(),
        description="This is an example recruiting instance.",
    )
    db_session.add(recruiting)
    db_session.commit()
    return recruiting


@pytest.fixture
def resume_questions(db_session: Session, recruiting: Recruiting):
    resume_questions = []
    for i in range(1, 3):
        resume_question = ResumeQuestion(
            recruiting_id=recruiting.id,
            question_num=i,
            content_limit=100,
            content=f"This is a test question {i}",
        )
        db_session.add(resume_question)
        resume_questions.append(resume_question)
    db_session.commit()
    return resume_questions


@pytest.fixture
def resume_repository(db_session: Session):
    return ResumeRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def user_repository(db_session: Session):
    return UserRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def user_service(user_repository: UserRepository):
    return UserService(user_repository=user_repository)


@pytest.fixture
def resume_service(resume_repository: ResumeRepository, user_service: UserService):
    return ResumeService(resume_repository=resume_repository, user_service=user_service)
