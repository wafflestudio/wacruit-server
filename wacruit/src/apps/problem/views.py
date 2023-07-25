from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.problem.exceptions import ProblemNotFoundException
from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.services import ProblemService
from wacruit.src.apps.user.dependencies import CurrentUser

v1_router = APIRouter(prefix="/v1/problems", tags=["problems"])


@v1_router.get("/{problem_id}", responses=responses_from(ProblemNotFoundException))
def get_problem(
    user: CurrentUser,
    problem_id: int,
    problem_service: Annotated[ProblemService, Depends()],
) -> ProblemResponse:
    return problem_service.get_problem(problem_id)


@v1_router.post("/submission", responses=responses_from(ProblemNotFoundException))
async def submit_code(
    user: CurrentUser,
    request: Request,
    code_submit_request: CodeSubmitRequest,
    problem_service: Annotated[ProblemService, Depends()],
):
    tokens, submission = await problem_service.submit_code(code_submit_request, user)
    return EventSourceResponse(
        problem_service.get_submission_result(
            request, tokens, submission, user, code_submit_request.is_example
        )
    )
