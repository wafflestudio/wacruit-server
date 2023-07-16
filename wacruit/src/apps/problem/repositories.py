from typing import Sequence

from fastapi import Depends
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import noload
from sqlalchemy.orm import Session

from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import CodeSubmissionToken
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import TestCase
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class ProblemRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_problems_by_recruiting_id(self, recruiting_id: int) -> Sequence[Problem]:
        query = (
            select(Problem)
            .where(Problem.recruiting_id == recruiting_id)
            .options(noload(Problem.testcases))
        )
        return self.session.execute(query).scalars().all()

    def get_problem_by_id_with_example_testcases(
        self, problem_id: int
    ) -> Problem | None:
        query = (
            select(Problem)
            .outerjoin(
                TestCase, (Problem.id == TestCase.problem_id) & TestCase.is_example
            )
            .where(Problem.id == problem_id)
            .options(contains_eager(Problem.testcases))
        )
        return self.session.execute(query).scalar()

    def get_testcases_by_problem_id(
        self, problem_id: int, is_example: bool = True
    ) -> Sequence[TestCase]:
        query = select(TestCase).where(
            TestCase.problem_id == problem_id, TestCase.is_example == is_example
        )
        return self.session.execute(query).scalars().all()

    def create_problem(self, problem: Problem) -> Problem:
        with self.transaction:
            self.session.add(problem)
        return problem


class CodeSubmissionRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_current_submission_by_user_id(self, user_id: int) -> CodeSubmission | None:
        query = (
            select(CodeSubmission)
            .where(CodeSubmission.user_id == user_id)
            .order_by(CodeSubmission.create_at.desc())
            .options(joinedload(CodeSubmission.tokens))
        )
        return self.session.execute(query).scalar()

    def create_submission(self, user_id: int, problem_id: int) -> CodeSubmission:
        code_submission = CodeSubmission(user_id=user_id, problem_id=problem_id)
        with self.transaction:
            self.session.add(code_submission)
        return code_submission

    def create_submission_tokens(self, submission_id, tokens: list[str]) -> None:
        with self.transaction:
            query = insert(CodeSubmissionToken).values(
                [{"submission_id": submission_id, "token": token} for token in tokens]
            )
            self.session.execute(query)
