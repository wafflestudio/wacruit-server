from typing import Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import join
from sqlalchemy.orm import Session

from wacruit.src.apps.problem.models import CodeSubmission
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

    def get_problems(self) -> list[Problem]:
        return self.session.query(Problem.id, Problem.body).all()  # type: ignore

    def get_problem_by_id(self, problem_id) -> Problem | None:
        return self.session.query(Problem).filter(Problem.id == problem_id).first()

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
