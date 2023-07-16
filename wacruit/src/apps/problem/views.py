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


@v1_router.post("/submission")
async def submit_code(
    request: Request,
    waffle_user_id: Annotated[str, Header()],
    code_submit_request: CodeSubmitRequest,
    problem_service: Annotated[ProblemService, Depends()],
):
    testcase_token_map = await problem_service.submit_code(code_submit_request)
    print(testcase_token_map)
    return EventSourceResponse(
        problem_service.get_submission_result(
            request, testcase_token_map, waffle_user_id
        )
    )
