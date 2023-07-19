import asyncio
from decimal import Decimal
from typing import Any, AsyncGenerator

from fastapi import Depends
from fastapi import Request
from sse_starlette import ServerSentEvent

from wacruit.src.apps.common.enums import JudgeSubmissionStatus
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.judge.schemas import JudgeCreateSubmissionRequest
from wacruit.src.apps.problem.exceptions import ProblemNotFoundException
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.schemas import CodeSubmissionResult
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
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

    async def submit_code(self, request: CodeSubmitRequest, user: User) -> list[str]:
        testcases = self.problem_repository.get_testcases_by_problem_id(
            request.problem_id, request.is_example
        )

        if not testcases:
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

        if not request.is_example:
            self.problem_repository.create_submission(
                user.id, request.problem_id, testcases, tokens
            )

        return tokens

    async def get_submission_result(
        self, request: Request, tokens: list[str], user: User, is_example: bool = True
    ) -> AsyncGenerator[ServerSentEvent, None]:
        token_map = dict(enumerate(tokens, start=1))

        while len(token_map) > 0:
            if await request.is_disconnected():
                break

            results = await self.judge_api_repository.get_batch_submissions(
                token_map.values()
            )
            responses = []
            for i, result in list(zip(token_map.keys(), results)):
                match result.status.id:
                    case (
                        JudgeSubmissionStatus.IN_QUEUE
                        | JudgeSubmissionStatus.PROCESSING
                    ):
                        continue
                    case JudgeSubmissionStatus.ACCEPTED:
                        ...  # TODO: 뭔가 성공했을 때 하는 로직
                    case _:
                        ...  # TODO: 뭔가 실패했을 때 하는 로직
                token_map.pop(i)

                responses.append(
                    CodeSubmissionResult(
                        num=i,
                        status=result.status,
                        stdout=result.stdout if is_example else None,
                        time=Decimal(result.time or 0),
                        memory=Decimal(result.memory or 0),
                    )
                )

            yield ServerSentEvent(
                data=ListResponse(items=responses).json(),
                event="message" if responses else "skip",
            )
            await asyncio.sleep(1)
