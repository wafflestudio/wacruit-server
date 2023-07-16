import asyncio
from typing import AsyncGenerator

from fastapi import Depends
from fastapi import Request
from sse_starlette import ServerSentEvent

from wacruit.src.apps.common.enums import JudgeSubmissionStatus
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.judge.schemas import JudgeCreateSubmissionRequest
from wacruit.src.apps.problem.exceptions import ProblemNotFoundException
from wacruit.src.apps.problem.models import TestCase
from wacruit.src.apps.problem.repositories import CodeSubmissionRepository
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.schemas import CodeSubmissionResult
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.schemas import TestCaseResponse
from wacruit.src.apps.user.models import User
from wacruit.src.utils.mixins import LoggingMixin


class ProblemService(LoggingMixin):
    def __init__(
        self,
        problem_repository: ProblemRepository = Depends(),
        code_submission_repository: CodeSubmissionRepository = Depends(),
        judge_api_repository: JudgeApiRepository = Depends(),
    ):
        self.problem_repository = problem_repository
        self.code_submission_repository = code_submission_repository
        self.judge_api_repository = judge_api_repository

    def get_all_problems(self, recruiting_id: int) -> list[ProblemResponse]:
        problems = self.problem_repository.get_problems_by_recruiting_id(recruiting_id)
        return ProblemResponse.from_orm_sequence(problems)

    def get_problem(self, problem_id: int) -> ProblemResponse:
        problem = self.problem_repository.get_problem_by_id_with_example_testcases(
            problem_id
        )
        if not problem:
            raise ProblemNotFoundException()
        return ProblemResponse.from_orm(problem)

    async def submit_code(self, request: CodeSubmitRequest, user: User) -> list[str]:
        testcases = list(
            self.problem_repository.get_testcases_by_problem_id(
                request.problem_id, request.is_test
            )
        )

        if request.is_test and request.extra_testcases:
            testcases = testcases + [
                TestCase(**tc.dict()) for tc in request.extra_testcases
            ]

        tokens: list[str] = []

        for i, testcase in enumerate(testcases, start=1):
            create_submission_request = JudgeCreateSubmissionRequest(
                problem_id=request.problem_id,
                source_code=request.source_code,
                language_id=request.language.value,
                stdin=testcase.stdin,
                expected_output=testcase.expected_output,
                cpu_time_limit=testcase.time_limit or 1.0,
            )
            token = (
                await self.judge_api_repository.create_submission(
                    create_submission_request
                )
            ).token
            tokens.append(token)

        if not request.is_test:
            code_submission = self.code_submission_repository.create_submission(
                user_id=user.id, problem_id=request.problem_id
            )
            self.code_submission_repository.create_submission_tokens(
                code_submission.id, tokens
            )

        return tokens

    async def get_submission_result(
        self,
        request: Request,
        tokens: list[str],
        is_test: bool,
    ) -> AsyncGenerator[ServerSentEvent, None]:
        start = 0
        while len(tokens) > start:
            if await request.is_disconnected():
                break

            results = []

            for i, token in enumerate(tokens, start=start):
                result = await self.judge_api_repository.get_submission(token)
                if result.status.id in (
                    JudgeSubmissionStatus.IN_QUEUE,
                    JudgeSubmissionStatus.PROCESSING,
                ):
                    break

                status = "FAILED"
                msg = ""
                if result.status.id == JudgeSubmissionStatus.ACCEPTED:
                    status = "SUCCESS"
                elif result.status.id == JudgeSubmissionStatus.WRONG_ANSWER:
                    msg = "틀렸습니다."
                elif result.status.id == JudgeSubmissionStatus.TIME_LIMIT_EXCEEDED:
                    msg = "시간 초과"
                elif result.status.id == JudgeSubmissionStatus.COMPILATION_ERROR:
                    msg = "컴파일 에러"
                elif result.status.id == JudgeSubmissionStatus.INTERNAL_ERROR:
                    msg = "서버 에러. 관리자에게 문의하세요."
                else:
                    msg = "런타임 에러"

                results.append(
                    CodeSubmissionResult(
                        id=i + 1,
                        status=status,
                        msg=msg,
                        stdout=result.stdout if is_test else None,
                        time=result.time,
                        memory=result.memory,
                    )
                )
                start += 1

            yield ServerSentEvent(data=ListResponse(items=results).dict())

            await asyncio.sleep(1)
