import asyncio
from decimal import Decimal
from typing import AsyncGenerator, List, Literal

from fastapi import Depends
from fastapi import Request

from wacruit.src.apps.common.enums import JudgeSubmissionStatus
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.judge.schemas import JudgeCreateSubmissionRequest
from wacruit.src.apps.judge.schemas import JudgeGetSubmissionResponse
from wacruit.src.apps.problem.repositories import CodeSubmissionRepository
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.schemas import CodeSubmissionResult
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
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

    def get_all_problems(self) -> list[ProblemResponse]:
        return [
            ProblemResponse(problem_num=i, body=p.body)
            for i, p in enumerate(self.problem_repository.get_problems(), start=1)
        ]

    async def submit_code(
        self,
        request: CodeSubmitRequest,
    ) -> list[str]:
        testcases = self.problem_repository.get_testcases_by_problem_id(
            request.problem_id
        )
        requests = [
            JudgeCreateSubmissionRequest(
                source_code=request.source_code,
                language_id=request.language.value,
                stdin=testcase.stdin,
                expected_output=testcase.expected_output,
                cpu_time_limit=float(testcase.time_limit),
                wall_time_limit=20,
            )
            for testcase in testcases
        ]
        response = await self.judge_api_repository.create_batch_submissions(requests)
        return [v.token for v in response]

    async def get_submission_result(
        self, request: Request, tokens: list[str], user_id: str
    ) -> AsyncGenerator[ListResponse[CodeSubmissionResult], None]:
        token_map = dict(enumerate(tokens, start=1))

        while len(token_map) > 0:
            if await request.is_disconnected():
                break

            results = await self.judge_api_repository.get_batch_submissions(
                token_map.values()
            )
            print(token_map)
            responses = []
            for i, result in list(zip(token_map.keys(), results)):
                match result.status.id:
                    case JudgeSubmissionStatus.IN_QUEUE | JudgeSubmissionStatus.PROCESSING:  # pylint: disable=line-too-long
                        continue
                    case JudgeSubmissionStatus.ACCEPTED:
                        ...  # 뭔가 성공했을 때 하는 로직
                    case _:
                        ...  # 뭔가 실패했을 때 하는 로직
                token_map.pop(i)

                responses.append(
                    CodeSubmissionResult(
                        num=i,
                        status=result.status,
                        stdout=result.stdout,
                        time=Decimal(result.time or 0),
                        memory=Decimal(result.memory or 0),
                    )
                )

            yield ListResponse(items=responses)
            await asyncio.sleep(1)

    async def check_submission(self, token: str) -> JudgeGetSubmissionResponse:
        return await self.judge_api_repository.get_submission(token)
