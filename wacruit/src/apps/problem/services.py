import asyncio
from typing import AsyncGenerator, Literal

from fastapi import Depends
from fastapi import Request

from wacruit.src.apps.common.enums import JudgeSubmissionStatus
from wacruit.src.apps.judge.repositories import JudgeApiRepository
from wacruit.src.apps.judge.schemas import JudgeCreateSubmissionRequest
from wacruit.src.apps.judge.schemas import JudgeGetSubmissionResponse
from wacruit.src.apps.problem.repositories import CodeSubmissionRepository
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.schemas import CodeSubmissionResult
from wacruit.src.apps.problem.schemas import CodeSubmissionResultResponse
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
    ) -> dict[int, str]:
        testcase_token_map = {}
        for i, testcase in enumerate(
            self.problem_repository.get_testcases_by_problem_id(
                request.problem_id
            ),  # type: ignore
            start=1,
        ):
            create_submission_request = JudgeCreateSubmissionRequest(
                problem_id=request.problem_id,
                source_code=request.source_code,
                language_id=request.language.value,
                stdin=testcase.stdin,
            )
            testcase_token_map[i] = (
                await self.judge_api_repository.create_submission(
                    create_submission_request
                )
            ).token
        return testcase_token_map

    async def get_submission_result(
        self, request: Request, testcase_token_map: dict[int, str], user_id: str
    ) -> AsyncGenerator[CodeSubmissionResultResponse, None]:
        running_testcases_set = set(testcase_token_map.keys())
        while len(running_testcases_set) > 0:
            if await request.is_disconnected():
                break
            results = []
            pending_testcases = []
            for testcase in running_testcases_set:
                result = await self.check_submission(testcase_token_map[testcase])
                if result.status.id in (
                    JudgeSubmissionStatus.IN_QUEUE,
                    JudgeSubmissionStatus.PROCESSING,
                ):
                    pending_testcases.append(testcase)
                else:
                    results.append(
                        CodeSubmissionResult(
                            id=testcase,
                            status=result.status,
                            result=f"{result.time},{result.memory}",
                        )
                    )
            running_testcases_set = set(pending_testcases)
            yield CodeSubmissionResultResponse(results=results)

            await asyncio.sleep(1)

    async def check_submission(self, token: str) -> JudgeGetSubmissionResponse:
        return await self.judge_api_repository.get_submission(token)
