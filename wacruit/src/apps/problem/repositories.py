from typing import Iterable, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import Session

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import CodeSubmissionResult
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

    def get_problem_by_id_with_example(self, problem_id: int) -> Problem | None:
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

    def create_submission(
        self,
        user_id: int,
        problem_id: int,
        language: Language,
        testcases: Iterable[TestCase],
        tokens: Iterable[str],
    ) -> CodeSubmission | None:
        with self.transaction:
            submission = CodeSubmission(
                user_id=user_id, problem_id=problem_id, language=language
            )
            self.session.add(submission)
            self.session.commit()
            results = (
                CodeSubmissionResult(
                    submission_id=submission.id, testcase_id=testcase.id, token=token
                )
                for testcase, token in zip(testcases, tokens)
            )
            self.session.bulk_save_objects(results)
            return submission

    def update_submission_status(
        self, submission: CodeSubmission, status: CodeSubmissionStatus
    ):
        with self.transaction:
            submission.status = status
            self.session.merge(submission)
