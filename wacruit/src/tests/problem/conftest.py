from httpx import AsyncClient
import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.judge import get_judge_api_client
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import TestCase
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.services import ProblemService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def problem(db_session: Session) -> Problem:
    p = Problem(num=1, body="1번 문제입니다.")
    db_session.add(p)
    db_session.commit()
    example_testcase = TestCase(
        problem_id=p.id,
        stdin="123",
        expected_output="12345",
        time_limit=1.0,
        is_example=True,
    )
    db_session.add(example_testcase)
    real_testcase = TestCase(
        problem_id=p.id,
        stdin="321",
        expected_output="54321",
        time_limit=2.0,
        is_example=False,
    )
    db_session.add(real_testcase)
    db_session.commit()
    return p


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
