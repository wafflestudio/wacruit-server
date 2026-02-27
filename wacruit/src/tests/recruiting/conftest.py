from datetime import datetime
from datetime import timedelta

import pytest

from wacruit.src.apps.common.security import PasswordService
from wacruit.src.apps.portfolio.file.services import PortfolioFileService
from wacruit.src.apps.portfolio.url.repositories import PortfolioUrlRepository
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import Testcase
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.services import RecruitingService
from wacruit.src.apps.resume.repositories import ResumeRepository
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.apps.user.services import UserService
from wacruit.src.database.connection import Session
from wacruit.src.database.connection import Transaction


@pytest.fixture
def recruiting(db_session: Session) -> Recruiting:
    recruiting = Recruiting(
        name="2023-루키-리크루팅",
        is_active=True,
        from_date=datetime.today() - timedelta(days=7),
        to_date=datetime.today() + timedelta(days=7),
        description="2023 루키 리크루팅입니다.",
        short_description="2023 루키 리크루팅",
    )
    db_session.add(recruiting)
    db_session.commit()

    problem = Problem(num=1, body="1번 문제입니다.", recruiting_id=recruiting.id)
    db_session.add(problem)
    db_session.commit()

    example_testcase = Testcase(
        problem_id=problem.id,
        stdin="example_input",
        expected_output="example_output",
        time_limit=1.0,
        is_example=True,
    )
    db_session.add(example_testcase)
    db_session.commit()

    real_testcase = Testcase(
        problem_id=problem.id,
        stdin="real_input",
        expected_output="real_output",
        time_limit=2.0,
        is_example=False,
    )
    db_session.add(real_testcase)
    db_session.commit()

    return recruiting


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(
        sso_id="abcdef123",
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="example@email.com",
        is_admin=False,
        password=PasswordService.hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()

    return user


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
def recruiting_repository(db_session: Session) -> RecruitingRepository:
    return RecruitingRepository(db_session, Transaction(db_session))


@pytest.fixture
def user_repository(db_session: Session):
    return UserRepository(db_session, Transaction(db_session))


@pytest.fixture
def user_service(user_repository: UserRepository):
    return UserService(user_repository)


@pytest.fixture
def resume_repository(db_session: Session):
    return ResumeRepository(db_session, Transaction(db_session))


@pytest.fixture
def resume_service(
    resume_repository: ResumeRepository,
    recruiting_repository: RecruitingRepository,
    user_service: UserService,
):
    return ResumeService(
        resume_repository,
        recruiting_repository,
        user_service,
    )


@pytest.fixture
def recruiting_service(
    portfolio_file_service: PortfolioFileService,
    portfolio_url_service: PortfolioUrlService,
    user_service: UserService,
    resume_service: ResumeService,
    recruiting_repository: RecruitingRepository,
) -> RecruitingService:
    return RecruitingService(
        portfolio_file_service,
        portfolio_url_service,
        user_service,
        resume_service,
        recruiting_repository,
    )
