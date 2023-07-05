import asyncio
from typing import AsyncGenerator, Literal

from fastapi import Depends
from fastapi import Request

from wacruit.src.api.schemas import CreateSubmissionRequest
from wacruit.src.apps.problem.repositories import CodeSubmissionRepository
from wacruit.src.apps.problem.repositories import JudgeApiRepository
from wacruit.src.apps.problem.repositories import ProblemRepository
from wacruit.src.apps.problem.schemas import CodeSubmissionResultResponse
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.schemas import TestCaseResult
from wacruit.src.utils.mixins import LoggingMixin

LANG_MAP = {
    "C": 100,
    "C++": 101,
    "JAVA": 102,
    "JAVASCRIPT": 103,
    "PYTHON": 104,
    "RUBY": 105,
    "GO": 106,
    "TYPESCRIPT": 107,
    "KOTLIN": 108,
    "SCALA": 109,
    "SQL": 110,
    "SWIFT": 111,
}


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

    async def get_all_problems(self) -> list[ProblemResponse]:
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
            create_submission_request = CreateSubmissionRequest(
                problem_id=request.problem_id,
                source_code=request.source_code,
                language_id=LANG_MAP[request.language.upper()],
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
                self.logger.debug("Request disconnected")
            results = []
            pending_testcases = []
            for testcase in running_testcases_set:
                result = await self.check_submission(testcase_token_map[testcase])
                if result:
                    results.append(TestCaseResult(id=testcase, result=result))
                else:
                    pending_testcases.append(testcase)
            running_testcases_set = set(pending_testcases)
            yield CodeSubmissionResultResponse(results=results)

            await asyncio.sleep(1)

    async def check_submission(self, token: str) -> str | Literal[False]:
        result = await self.judge_api_repository.get_submission(token)
        return (
            result.status.id == 3 and f"{result.time},{result.memory}"  # type: ignore
        )
