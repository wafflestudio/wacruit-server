import asyncio
from decimal import Decimal
import json
from typing import AsyncGenerator, Tuple

from fastapi import Depends
from fastapi import Request
from httpx import HTTPStatusError
from sse_starlette import ServerSentEvent

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import JudgeSubmissionStatus
from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.judge.schemas import JudgeCreateSubmissionRequest
from wacruit.src.apps.problem.exceptions import CodeSubmissionErrorException
from wacruit.src.apps.problem.exceptions import CodeSubmissionFailedException
from wacruit.src.apps.problem.exceptions import ProblemNotFoundException
from wacruit.src.apps.problem.exceptions import TestcaseNotFoundException
from wacruit.src.apps.problem.models import CodeSubmission
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.schemas import CodeSubmissionResult
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.schemas import TokenStr
from wacruit.src.apps.problem.utils import memory_handi
from wacruit.src.apps.problem.utils import time_handi
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
        problem = self.problem_repository.get_problem_by_id(problem_id, is_example=True)
        if problem is None:
            raise ProblemNotFoundException()
        return ProblemResponse.from_orm(problem)

    async def submit_code(
        self, request: CodeSubmitRequest, user: User
    ) -> Tuple[list[TokenStr], CodeSubmission | None]:
        problem = self.problem_repository.get_problem_by_id(
            request.problem_id, request.is_example
        )

        if problem is None:
            raise ProblemNotFoundException()

        testcases = problem.testcases

        if request.is_example:
            testcases = [*testcases, *request.extra_testcases]

        if len(testcases) == 0:
            raise TestcaseNotFoundException()

        requests = (
            [
                JudgeCreateSubmissionRequest(
                    source_code=request.source_code,
                    language_id=request.language.value,
                    stdin=testcase.stdin,
                    expected_output=testcase.expected_output,
                    cpu_time_limit=time_handi(1.0, request.language),
                    cpu_extra_time=0.0,
                    wall_time_limit=20.0,
                    memory_limit=memory_handi(10000, request.language),
                    stack_limit=64000,
                    compiler_options="-jvm-target 13"
                    if request.language == Language.KOTLIN
                    else None,
                )
                for testcase in testcases
            ]
            if request.is_example
            else [
                JudgeCreateSubmissionRequest(
                    source_code=request.source_code,
                    language_id=request.language.value,
                    stdin=testcase.stdin,
                    expected_output=testcase.expected_output,
                    cpu_time_limit=time_handi(
                        float(testcase.time_limit), request.language
                    ),
                    cpu_extra_time=float(testcase.extra_time),
                    wall_time_limit=20.0,
                    memory_limit=memory_handi(testcase.memory_limit, request.language),
                    stack_limit=testcase.stack_limit,
                    compiler_options="-jvm-target 13"
                    if request.language == Language.KOTLIN
                    else None,
                )
                for testcase in testcases
            ]
        )

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
        total_count = len(token_map)
        solve_count = 0
        error_count = 0
        wrong_count = 0
        disconnected = False

        while len(token_map) > 0:
            print(token_map)
            data = ""
            event = "skip"

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
                            solve_count += 1
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
                            wrong_count += 1
                        case (
                            JudgeSubmissionStatus.INTERNAL_ERROR
                            | JudgeSubmissionStatus.EXEC_FORMAT_ERROR
                        ):
                            raise CodeSubmissionErrorException(testcase_result)

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
                data = json.dumps(
                    {"detail": "채점 서버에 일시적인 문제가 생겼습니다. 잠시 후 다시 시도해주세요."},
                    ensure_ascii=False,
                )
                event = "error"
                print(e)
                token_map = {}
                error_count += 1
            except CodeSubmissionErrorException as e:
                data = json.dumps({"detail": e.detail}, ensure_ascii=False)
                event = "error"
                print(e)
                token_map = {}
                error_count += 1
            finally:
                if not disconnected:
                    yield ServerSentEvent(data=data, event=event)
                    disconnected = await request.is_disconnected()
                await asyncio.sleep(1)

        status = self.check_submission_reuslt(
            total_count, solve_count, wrong_count, error_count
        )

        if submission is not None:
            self.problem_repository.update_submission_status(submission, status)

    def check_submission_reuslt(
        self, total_count, solve_count, wrong_count, error_count
    ) -> CodeSubmissionStatus:
        if total_count == solve_count:
            status = CodeSubmissionStatus.SOLVED
        elif error_count > 0:
            status = CodeSubmissionStatus.ERROR
        elif wrong_count > 0:
            status = CodeSubmissionStatus.WRONG
        else:
            status = CodeSubmissionStatus.ERROR
        return status
