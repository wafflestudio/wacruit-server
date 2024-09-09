from datetime import timedelta
from typing import Iterable, Sequence, Tuple

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed

from wacruit.src.apps.common.enums import CodeSubmissionResultStatus
from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import CodeSubmissionResult
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import Testcase
from wacruit.src.database.asyncio.connection import AsyncTransaction
from wacruit.src.database.asyncio.connection import get_db_session
from wacruit.src.utils.mixins import LoggingMixin


class ProblemRepository(LoggingMixin):
    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        transaction: AsyncTransaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    async def get_problem_by_id(
        self, problem_id: int, is_example: bool
    ) -> Problem | None:
        query = (
            select(Problem)
            .outerjoin(
                Testcase,
                (Problem.id == Testcase.problem_id)
                & (Testcase.is_example == is_example),
            )
            .where(Problem.id == problem_id)
            .options(contains_eager(Problem.testcases))
            .options(joinedload(Problem.recruiting))
        )
        return (await self.session.execute(query)).scalar()

    async def create_submission(
        self,
        user_id: int,
        problem_id: int,
        language: Language,
        source_code: str,
        testcases: Iterable[Testcase],
    ) -> Tuple[CodeSubmission, list[CodeSubmissionResult]] | None:
        submission = None
        async with self.transaction:
            submission = CodeSubmission(
                user_id=user_id,
                problem_id=problem_id,
                language=language,
                source_code=source_code,
            )
            self.session.add(submission)
            # await self.session.commit()
        if submission is None:
            return None
        async with self.transaction:
            results = [
                CodeSubmissionResult(
                    submission_id=submission.id, testcase_id=testcase.id, token=""
                )
                for testcase in testcases
            ]
            self.session.add_all(results)
            # await self.session.commit()
            return submission, results

    async def get_recent_submission(
        self, user_id: int, problem_id: int
    ) -> CodeSubmission | None:
        query = (
            select(CodeSubmission)
            .where(
                (CodeSubmission.user_id == user_id)
                & (CodeSubmission.problem_id == problem_id)
            )
            .order_by(CodeSubmission.created_at.desc())
            .options(
                joinedload(CodeSubmission.results).joinedload(
                    CodeSubmissionResult.testcase
                )
            )
        )
        return (await self.session.execute(query)).scalar()

    async def get_submission_result(
        self, submission_id: int, testcase_id: int
    ) -> CodeSubmissionResult | None:
        query = select(CodeSubmissionResult).where(
            (CodeSubmissionResult.submission_id == submission_id)
            & (CodeSubmissionResult.testcase_id == testcase_id)
        )
        return (await self.session.execute(query)).scalar()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(timedelta(seconds=1)))
    async def update_submission_status(
        self, submission: CodeSubmission, status: CodeSubmissionStatus
    ):
        async with self.transaction:
            submission.status = status
            await self.session.merge(submission)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(timedelta(seconds=1)))
    async def update_submission_result(
        self,
        submission_result: CodeSubmissionResult,
        status: CodeSubmissionResultStatus,
        time: float | None,
        memory: int | None,
    ):
        async with self.transaction:
            submission_result.status = status
            submission_result.time = time
            submission_result.memory = memory
            await self.session.merge(submission_result)
