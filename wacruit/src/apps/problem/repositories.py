from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.orm import Session

from wacruit.src.api.connections import get_api_client
from wacruit.src.api.schemas import CreateSubmissionRequest
from wacruit.src.api.schemas import CreateSubmissionResponse
from wacruit.src.api.schemas import GetSubmissionResponse
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import TestCase
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class JudgeApiRepository:
    def __init__(self, client: AsyncClient = Depends(get_api_client("JUDGE"))):
        self.client = client

    async def create_submission(
        self, request: CreateSubmissionRequest
    ) -> CreateSubmissionResponse:
        res = await self.client.post(
            url="/submissions?base64_encoded=false", data=request.dict(), timeout=60
        )
        res.raise_for_status()
        return CreateSubmissionResponse(**res.json())

    async def list_submission(self, fields: list[str]) -> GetSubmissionResponse:
        res = await self.client.get(
            url="/submissions?base64_encoded=false",
            params={"fields": ",".join(fields)},
            timeout=60,
        )
        res.raise_for_status()
        return GetSubmissionResponse(**res.json())

    async def get_submission(
        self, token: str, fields: list[str] | None = None
    ) -> GetSubmissionResponse:
        res = await self.client.get(
            url=f"/submissions/{token}?base64_encoded=false",
            params=fields and {"fields": ",".join(fields)},  # type: ignore
            timeout=60,
        )
        res.raise_for_status()
        return GetSubmissionResponse(**res.json())


class ProblemRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_problems(self) -> list[Problem]:
        return self.session.query(Problem.id, Problem.body).all()  # type: ignore

    def get_problem_by_id(self, problem_id) -> Problem | None:
        return self.session.query(Problem).filter(Problem.id == problem_id).first()

    def get_testcases_by_problem_id(self, problem_id) -> list[TestCase]:
        problem = self.get_problem_by_id(problem_id)
        return problem.testcases if problem else []

    def create_problem(self, problem: Problem) -> Problem:
        with self.transaction:
            self.session.add(problem)
        return problem

    def create_problems(self, problems: list[Problem]) -> None:
        with self.transaction:
            self.session.bulk_save_objects(problems)


class CodeSubmissionRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_submissions(self) -> list[CodeSubmission]:
        return self.session.query(CodeSubmission).all()

    def get_submission_by_id(self, submission_id):
        return (
            self.session.query(CodeSubmission)
            .filter(CodeSubmission.id == submission_id)
            .first()
        )

    def create_submission(self, submission: CodeSubmission):
        with self.transaction:
            self.session.add(submission)
        return submission
