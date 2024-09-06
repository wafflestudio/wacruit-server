from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.exceptions import RecruitingAlreadyAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.recruiting.schemas import RecruitingResultResponse
from wacruit.src.apps.recruiting.schemas import RecruitingSummaryResponse
from wacruit.src.apps.recruiting.services import RecruitingService
from wacruit.src.apps.user.dependencies import CurrentUser

v1_router = APIRouter(prefix="/v1/recruitings", tags=["recruitings"])


@v1_router.get("")
def list_recruitings(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingSummaryResponse]:
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


@v1_router.get(
    "/{recruiting_id}/result", responses=responses_from(RecruitingNotAppliedException)
)
def get_recruiting_result(
    user: CurrentUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> RecruitingResultResponse:
    return recruiting_service.get_recruiting_result_by_id(recruiting_id, user)


@v1_router.post(
    "/{recruiting_id}/apply",
    responses=responses_from(
        RecruitingNotFoundException, RecruitingAlreadyAppliedException
    ),
)
def apply_recruiting(
    user: CurrentUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> Response:
    recruiting_service.apply_recruiting(recruiting_id, user)
    return Response(status_code=204)


@v1_router.delete(
    "/{recruiting_id}/apply",
    responses=responses_from(
        RecruitingNotFoundException, RecruitingNotAppliedException
    ),
)
async def cancel_recruiting(
    user: CurrentUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> Response:
    await recruiting_service.cancel_recruiting(recruiting_id, user)
    return Response(status_code=204)
