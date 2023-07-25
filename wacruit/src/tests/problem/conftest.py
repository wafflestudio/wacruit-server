from datetime import datetime
from datetime import timedelta

from httpx import AsyncClient
import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.judge import get_judge_api_client
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import TestCase
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.services import ProblemService
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.database.connection import Transaction


@pytest.fixture
def problem(db_session: Session) -> Problem:
    recruiting = Recruiting(
        name="2023-루키-리크루팅",
        is_active=True,
        from_date=datetime.today() - timedelta(days=7),
        to_date=datetime.today() + timedelta(days=7),
        description="2023 루키 리크루팅입니다.",
    )
    db_session.add(recruiting)
    db_session.commit()

    problem = Problem(num=1, body="1번 문제입니다.", recruiting_id=recruiting.id)
    db_session.add(problem)
    db_session.commit()

    example_testcase = TestCase(
        problem_id=problem.id,
        stdin="example_input",
        expected_output="example_output",
        time_limit=1.0,
        is_example=True,
    )
    db_session.add(example_testcase)
    db_session.commit()

    real_testcase = TestCase(
        problem_id=problem.id,
        stdin="real_input",
        expected_output="real_output",
        time_limit=2.0,
        is_example=False,
    )
    db_session.add(real_testcase)
    db_session.commit()

    return problem


@pytest.fixture
def problem_repository(db_session: Session):
    return ProblemRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
async def judge_api_client():
    return await anext(get_judge_api_client())


@pytest.fixture
def judge_api_repository(judge_api_client: AsyncClient):
    return JudgeApiRepository(client=judge_api_client)


@pytest.fixture
def problem_service(
    problem_repository: ProblemRepository,
    judge_api_repository: JudgeApiRepository,
):
    return ProblemService(
        problem_repository=problem_repository,
        judge_api_repository=judge_api_repository,
    )
