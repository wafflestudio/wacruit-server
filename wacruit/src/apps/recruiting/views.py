from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.schemas import RecruitingApplicantDto
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.recruiting.services import RecruitingService
from wacruit.src.apps.user.dependencies import CurrentUser

v1_router = APIRouter(prefix="/v1/recruitings", tags=["recruitings"])


@v1_router.get("")
def list_recruitings(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingApplicantDto]:
    return recruiting_service.get_all_recruiting()


@v1_router.get(
    "/{recruiting_id}", responses=responses_from(RecruitingNotFoundException)
)
def get_recruiting(
    user: CurrentUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> RecruitingResponse:
    return recruiting_service.get_recruiting_by_id(recruiting_id, user)
