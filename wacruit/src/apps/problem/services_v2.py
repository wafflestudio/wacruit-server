import asyncio
from typing import AsyncGenerator
from typing import Literal

from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import Request
from sse_starlette import ServerSentEvent

from wacruit.src.apps.common.enums import CodeSubmissionResultStatus
from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.hodu.repositories import HoduApiRepository
from wacruit.src.apps.hodu.schemas import HoduField
from wacruit.src.apps.hodu.schemas import HoduSubmitErrorResponse
from wacruit.src.apps.hodu.schemas import HoduSubmitRequest
from wacruit.src.apps.hodu.schemas import HoduSubmitResponse
from wacruit.src.apps.hodu.schemas import HoduSubmitStatus
from wacruit.src.apps.problem.exceptions import CodeSubmissionFailedException
from wacruit.src.apps.problem.exceptions import NoRecentSubmissionException
from wacruit.src.apps.problem.exceptions import ProblemNotFoundException
from wacruit.src.apps.problem.exceptions import TestcaseNotFoundException
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.models import CodeSubmissionResult
from wacruit.src.apps.problem.repositories_v2 import ProblemRepository
from wacruit.src.apps.problem.schemas_v2 import CodeSubmissionErrorResponse
from wacruit.src.apps.problem.schemas_v2 import CodeSubmissionResultResponse
from wacruit.src.apps.problem.schemas_v2 import CodeSubmitRequest
from wacruit.src.apps.problem.schemas_v2 import ProblemResponse
from wacruit.src.apps.problem.utils_v2 import memory_handi
from wacruit.src.apps.problem.utils_v2 import time_handi
from wacruit.src.apps.recruiting.exceptions import RecruitingClosedException
from wacruit.src.apps.user.models import User
from wacruit.src.utils.mixins import LoggingMixin


class ProblemService(LoggingMixin):
    def __init__(
        self,
        background_tasks: BackgroundTasks,
        problem_repository: ProblemRepository = Depends(),
        hodu_api_repository: HoduApiRepository = Depends(),
    ):
        self.background_tasks = background_tasks
        self.problem_repository = problem_repository
        self.hodu_api_repository = hodu_api_repository

    def get_problem(self, problem_id) -> ProblemResponse:
        problem = self.problem_repository.get_problem_by_id(problem_id, is_example=True)
        if problem is None:
            raise ProblemNotFoundException()
        return ProblemResponse.from_orm(problem)

    async def submit_code(self, request: CodeSubmitRequest, user: User) -> None:
        problem = self.problem_repository.get_problem_by_id(
            request.problem_id, request.is_example
        )

        if problem is None:
            raise ProblemNotFoundException()

        if not problem.recruiting.is_open:
            raise RecruitingClosedException()

        testcases = problem.testcases

        if request.is_example:
            testcases = [*testcases, *request.extra_testcases]

        if len(testcases) == 0:
            raise TestcaseNotFoundException()

        hodu_requests = (
            [
                HoduSubmitRequest(
                    code=request.source_code,
                    language=request.language,
                    stdin=testcase.stdin,
                    expected_stdout=testcase.expected_output,
                    time_limit=time_handi(1.0, request.language),
                    memory_limit=memory_handi(10000, request.language),
                    fields=[HoduField.WILDCARD],
                )
                for testcase in testcases
            ]
            if request.is_example
            else [
                HoduSubmitRequest(
                    code=request.source_code,
                    language=request.language,
                    stdin=testcase.stdin,
                    expected_stdout=testcase.expected_output,
                    time_limit=time_handi(float(testcase.time_limit), request.language),
                    memory_limit=memory_handi(testcase.memory_limit, request.language),
                    fields=[HoduField.WILDCARD],
                )
                for testcase in testcases
            ]
        )

        if not request.is_example:
            submission_and_results = self.problem_repository.create_submission(
                user.id,
                request.problem_id,
                request.language.to_language(),
                request.source_code,
                testcases,
            )

            if submission_and_results is None:
                raise CodeSubmissionFailedException()

            submission, results = submission_and_results

            self.background_tasks.add_task(
                self.record_submission_results,
                submission,
                results,
                hodu_requests,
            )

    async def record_submission_results(
        self,
        submission: CodeSubmission,
        results: list[CodeSubmissionResult],
        hodu_requests: list[HoduSubmitRequest],
    ) -> None:
        total_status = CodeSubmissionStatus.SOLVED

        def merge_status(
            status: Literal[CodeSubmissionStatus.ERROR]
            | Literal[CodeSubmissionStatus.WRONG],
        ):
            nonlocal total_status
            if status == CodeSubmissionStatus.ERROR:
                total_status = CodeSubmissionStatus.ERROR
            elif status == CodeSubmissionStatus.WRONG:
                if total_status == CodeSubmissionStatus.SOLVED:
                    total_status = CodeSubmissionStatus.WRONG

        for index, (submission_result, hodu_request) in enumerate(
            zip(results, hodu_requests)
        ):
            response = await self.hodu_api_repository.submit(hodu_request)
            if isinstance(response, HoduSubmitResponse):
                submission_result_status = response.status.to_submission_result_status()
                if submission_result_status not in (
                    CodeSubmissionResultStatus.CORRECT,
                    CodeSubmissionResultStatus.INTERNAL_SERVER_ERROR,
                ):
                    print("############################################")
                    print(f"hodu_request: {hodu_request.json()}")
                    print(f"status: {response.status}")
                    print(f"stdout: {response.fields.stdout}")
                    print(f"stderr: {response.fields.stderr}")
                    print("\n\n")
                    merge_status(CodeSubmissionStatus.WRONG)
                elif (
                    submission_result_status
                    == CodeSubmissionResultStatus.INTERNAL_SERVER_ERROR
                ):
                    merge_status(CodeSubmissionStatus.ERROR)
                self.problem_repository.update_submission_result(
                    submission_result,
                    submission_result_status,
                    response.fields.time,
                    response.fields.memory,
                )
            elif isinstance(response, HoduSubmitErrorResponse):
                merge_status(CodeSubmissionStatus.ERROR)
                self.logger.error("HODU submission failed: %s", response.detail)
                for pending_result in results[index:]:
                    self.problem_repository.update_submission_result(
                        pending_result,
                        CodeSubmissionResultStatus.INTERNAL_SERVER_ERROR,
                        None,
                        None,
                    )
                break

        self.problem_repository.update_submission_status(submission, total_status)

    async def get_recent_submission_result(
        self,
        request: Request,
        user: User,
        problem_id: int,
    ) -> AsyncGenerator[ServerSentEvent, None]:
        problem = self.problem_repository.get_problem_by_id(problem_id, is_example=True)

        if problem is None:
            raise ProblemNotFoundException()

        recent_submission = self.problem_repository.get_recent_submission(
            user.id, problem_id
        )

        if recent_submission is None:
            raise NoRecentSubmissionException()

        results = recent_submission.results
        return_count = 0

        while return_count < len(results):
            if await request.is_disconnected():
                return

            partial_responses = []
            judge_failed = False
            for result in results[return_count:]:
                if result.status == CodeSubmissionResultStatus.RUNNING:
                    break
                if result.status == CodeSubmissionResultStatus.INTERNAL_SERVER_ERROR:
                    judge_failed = True
                    break

                return_count += 1
                partial_responses.append(
                    CodeSubmissionResultResponse(
                        num=result.testcase.id,
                        status=HoduSubmitStatus.from_submission_result_status(
                            result.status
                        ),
                        time=result.time,
                        memory=result.memory,
                    )
                )

            if partial_responses:
                yield ServerSentEvent(
                    data=ListResponse(items=partial_responses).json(), event="message"
                )

            if judge_failed:
                yield ServerSentEvent(
                    data=CodeSubmissionErrorResponse().json(ensure_ascii=False),
                    event="error",
                )
                return

            if return_count == len(results):
                return
            if not partial_responses:
                yield ServerSentEvent(data=ListResponse(items=[]).json(), event="skip")
            if await request.is_disconnected():
                return

            await asyncio.sleep(1)
            self.problem_repository.session.expire_all()
            self.problem_repository.session.commit()
            recent_submission = (
                self.problem_repository.get_recent_submission(user.id, problem_id)
                or recent_submission
            )
            results = recent_submission.results
