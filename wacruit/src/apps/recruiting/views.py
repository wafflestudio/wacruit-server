from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.problem.schemas import ProblemResponse
from wacruit.src.apps.problem.services import ProblemService

v1_router = APIRouter(prefix="/v1/recruiting", tags=["recruiting"])


@v1_router.get("/{recruiting_id}/problem")
def list_problem(
    recruiting_id: int,
    problem_service: Annotated[ProblemService, Depends()],
) -> list[ProblemResponse]:
    return problem_service.get_all_problems(recruiting_id)
