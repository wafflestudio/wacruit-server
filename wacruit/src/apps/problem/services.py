import asyncio
from decimal import Decimal
from typing import Any, AsyncGenerator, Tuple

from fastapi import Depends
from fastapi import Request
from httpx import HTTPStatusError
from sse_starlette import ServerSentEvent

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import JudgeSubmissionStatus
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.judge.schemas import JudgeCreateSubmissionRequest
from wacruit.src.apps.problem.exceptions import CodeSubmissionErrorException
from wacruit.src.apps.problem.exceptions import CodeSubmissionFailedException
from wacruit.src.apps.problem.exceptions import ProblemNotFoundException
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.schemas import CodeSubmissionResult
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.schemas import TokenStr
from wacruit.src.apps.user.models import User
from wacruit.src.utils.mixins import LoggingMixin


class ProblemService(LoggingMixin):
    def __init__(
        self,
        problem_repository: ProblemRepository = Depends(),
        judge_api_repository: JudgeApiRepository = Depends(),
    ):
        self.problem_repository = problem_repository
        self.judge_api_repository = judge_api_repository

    def get_problem(self, problem_id) -> ProblemResponse:
        problem = self.problem_repository.get_problem_by_id_with_example(problem_id)
        if problem is None:
            raise ProblemNotFoundException()
        return ProblemResponse.from_orm(problem)

    async def submit_code(
        self, request: CodeSubmitRequest, user: User
    ) -> Tuple[list[TokenStr], CodeSubmission | None]:
        testcases = self.problem_repository.get_testcases_by_problem_id(
            request.problem_id, request.is_example
        )

        if not testcases and (not request.is_example or not request.extra_testcases):
            raise ProblemNotFoundException()

        if request.is_example and request.extra_testcases:
            testcases = [*testcases, *request.extra_testcases]

        requests = [
            JudgeCreateSubmissionRequest(
                source_code=request.source_code,
                language_id=request.language.value,
                stdin=testcase.stdin,
                expected_output=testcase.expected_output,
                cpu_time_limit=1.0
                if request.is_example
                else float(testcase.time_limit),
                wall_time_limit=20.0,
            )
            for testcase in testcases
        ]

        response = await self.judge_api_repository.create_batch_submissions(requests)
        tokens = [v.token for v in response]
        submission = None

        if not request.is_example:
            submission = self.problem_repository.create_submission(
                user.id,
                request.problem_id,
                request.language,
                testcases,
                tokens,
            )

            if submission is None:
                raise CodeSubmissionFailedException()

        return tokens, submission

    async def get_submission_result(
        self,
        request: Request,
        tokens: list[TokenStr],
        submission: CodeSubmission | None,
        user: User,
        is_example: bool = True,
    ) -> AsyncGenerator[ServerSentEvent, None]:
        token_map = dict(enumerate(tokens, start=1))
        status = CodeSubmissionStatus.SOLVED

        while len(token_map) > 0:
            data = ""
            event = "skip"

            if await request.is_disconnected():
                break

            try:
                testcase_results = (
                    await self.judge_api_repository.get_batch_submissions(
                        token_map.values()
                    )
                )
                responses = []
                for i, testcase_result in list(zip(token_map.keys(), testcase_results)):
                    match testcase_result.status.id:
                        case (
                            JudgeSubmissionStatus.IN_QUEUE
                            | JudgeSubmissionStatus.PROCESSING
                        ):
                            continue
                        case JudgeSubmissionStatus.ACCEPTED:
                            ...
                        case (
                            JudgeSubmissionStatus.WRONG_ANSWER
                            | JudgeSubmissionStatus.TIME_LIMIT_EXCEEDED
                            | JudgeSubmissionStatus.COMPILATION_ERROR
                            | JudgeSubmissionStatus.RUNTIME_ERROR_SIGSEGV
                            | JudgeSubmissionStatus.RUNTIME_ERROR_SIGXFSZ
                            | JudgeSubmissionStatus.RUNTIME_ERROR_SIGFPE
                            | JudgeSubmissionStatus.RUNTIME_ERROR_SIGABRT
                            | JudgeSubmissionStatus.RUNTIME_ERROR_NZEC
                            | JudgeSubmissionStatus.RUNTIME_ERROR_OTHER
                        ):
                            status = CodeSubmissionStatus.WRONG
                        case (
                            JudgeSubmissionStatus.INTERNAL_ERROR
                            | JudgeSubmissionStatus.EXEC_FORMAT_ERROR
                        ):
                            raise CodeSubmissionErrorException()

                    token_map.pop(i)

                    responses.append(
                        CodeSubmissionResult(
                            num=i,
                            status=testcase_result.status,
                            stdout=testcase_result.stdout if is_example else None,
                            time=Decimal(testcase_result.time or 0),
                            memory=Decimal(testcase_result.memory or 0),
                        )
                    )

                data = ListResponse(items=responses).json()
                if responses:
                    event = "message"

            except HTTPStatusError as e:
                data = {"detail": "채점 서버에 일시적인 문제가 생겼습니다. 잠시 후 다시 시도해주세요."}
                event = "error"
                token_map = {}
            except CodeSubmissionErrorException as e:
                data = {"detail": e.detail}
                event = "error"
                token_map = {}
            finally:
                yield ServerSentEvent(data=data, event=event)
                await asyncio.sleep(1)

        if submission is not None:
            self.problem_repository.update_submission_status(submission, status)
