from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.problem.exceptions import CodeSubmissionFailedException
from wacruit.src.apps.problem.exceptions import NoRecentSubmissionException
from wacruit.src.apps.problem.exceptions import ProblemNotFoundException
from wacruit.src.apps.problem.exceptions import TestcaseNotFoundException
from wacruit.src.apps.problem.schemas_v2 import CodeSubmitRequest
from wacruit.src.apps.problem.schemas_v2 import ProblemResponse
from wacruit.src.apps.problem.services_v2 import ProblemService
from wacruit.src.apps.recruiting.exceptions import RecruitingClosedException
from wacruit.src.apps.user.dependencies import CurrentUser

v2_router = APIRouter(prefix="/v2/problems", tags=["problems"])


@v2_router.get("/{problem_id}", responses=responses_from(ProblemNotFoundException))
def get_problem(
    user: CurrentUser,
    problem_id: int,
    problem_service: Annotated[ProblemService, Depends()],
) -> ProblemResponse:
    return problem_service.get_problem(problem_id)


@v2_router.post(
    "/submission",
    responses=responses_from(
        ProblemNotFoundException,
        RecruitingClosedException,
        TestcaseNotFoundException,
        CodeSubmissionFailedException,
    ),
)
async def submit_code(
    user: CurrentUser,
    request: Request,
    code_submit_request: CodeSubmitRequest,
    problem_service: Annotated[ProblemService, Depends()],
):
    await problem_service.submit_code(code_submit_request, user)
    return {"message": "코드 제출이 완료되었습니다."}


@v2_router.get(
    "/{problem_id}/submission",
    responses=responses_from(ProblemNotFoundException, NoRecentSubmissionException),
)
async def get_submission(
    user: CurrentUser,
    request: Request,
    problem_id: int,
    problem_service: Annotated[ProblemService, Depends()],
):
    return EventSourceResponse(
        problem_service.get_recent_submission_result(request, user, problem_id),
        ping=3600,
    )
