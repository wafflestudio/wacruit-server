from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from wacruit.src.apps.problem.schemas import CodeSubmitRequest
from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.services import ProblemService

v1_router = APIRouter(prefix="/v1/problem", tags=["problem"])


@v1_router.get("/{problem_id}")
def get_problem(
    problem_id: int,
    problem_service: Annotated[ProblemService, Depends()],
) -> ProblemResponse:
    return problem_service.get_problem(problem_id)


@v1_router.post("/submission")
async def submit_code(
    request: Request,
    waffle_user_id: Annotated[str, Header()],
    code_submit_request: CodeSubmitRequest,
    problem_service: Annotated[ProblemService, Depends()],
):
    tokens = await problem_service.submit_code(code_submit_request)
    return EventSourceResponse(
        problem_service.get_submission_result(
            request, tokens, waffle_user_id, code_submit_request.is_test
        )
    )
