from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from wacruit.src.apps.common.dependencies import CurrentUser
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.services import ProblemService

v1_router = APIRouter(prefix="/v1/problem", tags=["problem"])


@v1_router.get("/{problem_id}")
def get_problem(
    user: CurrentUser,
    problem_id: int,
    problem_service: Annotated[ProblemService, Depends()],
) -> ProblemResponse:
    return problem_service.get_problem(problem_id)


@v1_router.post("/submission")
async def submit_code(
    request: Request,
    user: CurrentUser,
    code_submit_request: CodeSubmitRequest,
    problem_service: Annotated[ProblemService, Depends()],
):
    testcase_token = await problem_service.submit_code(code_submit_request, user)
    return EventSourceResponse(
        problem_service.get_submission_result(
            request, testcase_token, code_submit_request.is_test
        )
    )
