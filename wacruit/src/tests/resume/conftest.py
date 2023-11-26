from datetime import datetime
from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.portfolio.file.services_v2 import PortfolioFileService
from wacruit.src.apps.portfolio.url.repositories import PortfolioUrlRepository
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
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
def opened_recruiting(db_session: Session):
    recruiting = Recruiting(
        name="Example Recruiting",
        is_active=True,
        from_date=datetime.utcnow() + timedelta(days=-1),
        to_date=datetime.utcnow() + timedelta(days=1),
        description="This is an example recruiting instance.",
    )
    db_session.add(recruiting)
    db_session.commit()
    return recruiting


@pytest.fixture
def closed_recruiting(db_session: Session):
    recruiting = Recruiting(
        name="Example Recruiting",
        is_active=False,
        from_date=datetime.utcnow() + timedelta(days=-3),
        to_date=datetime.utcnow() + timedelta(days=-1),
        description="This is an example recruiting instance.",
    )
    db_session.add(recruiting)
    db_session.commit()
    return recruiting


@pytest.fixture
def resume_questions(db_session: Session, opened_recruiting: Recruiting):
    resume_questions = []
    for i in range(1, 3):
        resume_question = ResumeQuestion(
            recruiting_id=opened_recruiting.id,
            question_num=i,
            content_limit=100,
            content=f"This is a test question {i}",
        )
        db_session.add(resume_question)
        resume_questions.append(resume_question)
    db_session.commit()
    return resume_questions


@pytest.fixture
def portfolio_file_service():
    return PortfolioFileService()


@pytest.fixture
def portfolio_url_repository(db_session: Session):
    return PortfolioUrlRepository(
        session=db_session, transaction=Transaction(db_session)
    )


@pytest.fixture
def portfolio_url_service(
    portfolio_url_repository: PortfolioUrlRepository,
    recruiting_repository: RecruitingRepository,
):
    return PortfolioUrlService(
        portfolio_url_repository=portfolio_url_repository,
        recruiting_repository=recruiting_repository,
    )


@pytest.fixture
def user_repository(db_session: Session):
    return UserRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def user_service(user_repository: UserRepository):
    return UserService(user_repository=user_repository)


@pytest.fixture
def recruiting_repository(db_session: Session) -> RecruitingRepository:
    return RecruitingRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def resume_repository(db_session: Session):
    return ResumeRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def resume_service(
    portfolio_file_service: PortfolioFileService,
    portfolio_url_service: PortfolioUrlService,
    resume_repository: ResumeRepository,
    recruiting_repository: RecruitingRepository,
    user_service: UserService,
):
    return ResumeService(
        portfolio_file_service=portfolio_file_service,
        portfolio_url_service=portfolio_url_service,
        resume_repository=resume_repository,
        recruiting_repository=recruiting_repository,
        user_service=user_service,
    )
