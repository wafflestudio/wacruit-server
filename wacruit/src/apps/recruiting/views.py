from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.exceptions import RecruitingAlreadyAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.schemas import RecruitingCreateRequest
from wacruit.src.apps.recruiting.schemas import RecruitingUpdateRequest
from wacruit.src.apps.recruiting.schemas import UserRecruitingResponse
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.recruiting.schemas import RecruitingResultResponse
from wacruit.src.apps.recruiting.schemas import RecruitingSummaryResponse
from wacruit.src.apps.recruiting.schemas import RecruitingInfoResponse
from wacruit.src.apps.recruiting.services import RecruitingService
from wacruit.src.apps.user.dependencies import CurrentUser
from wacruit.src.apps.user.dependencies import AdminUser

from wacruit.src.apps.common.enums import RecruitingType

v1_router = APIRouter(prefix="/v1/recruitings", tags=["recruitings"])


@v1_router.get("")
def list_recruitings(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingSummaryResponse]:
    return recruiting_service.get_all_recruiting()

@v1_router.post("/")
def create_recruiting(
    admin_user: AdminUser,
    recruiting_service: Annotated[RecruitingService, Depends()],
    request: RecruitingCreateRequest
) -> RecruitingResponse:
    return recruiting_service.create_recruiting(request)

@v1_router.get("/active")
def get_active_recruitings(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingSummaryResponse]:
    return recruiting_service.get_active_recruitings()

@v1_router.get("/by-type")
def get_recruitings_by_type(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingInfoResponse]:
    items = []
    for recruiting_type in RecruitingType.__members__.values():
        result = recruiting_service.get_recruiting_info_by_type(recruiting_type)
        if result is not None:
            items.append(result)
    return ListResponse(items=items)

@v1_router.get(
    "/{recruiting_id}/user", responses=responses_from(RecruitingNotFoundException)
)
def get_user_recruiting(
    user: CurrentUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> UserRecruitingResponse:
    return recruiting_service.get_recruiting_by_id(recruiting_id, user)

@v1_router.patch("/{recruiting_id}")
def update_recruiting(
    admin_user: AdminUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
    request: RecruitingUpdateRequest
) -> RecruitingResponse:
    return recruiting_service.update_recruiting(recruiting_id, request)

@v1_router.get("/{recruiting_id}")
def get_recruiting_by_id(
    admin_user: AdminUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> RecruitingResponse:
    return recruiting_service.get_recruitings_by_id(recruiting_id)

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
def cancel_recruiting(
    user: CurrentUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> Response:
    recruiting_service.cancel_recruiting(recruiting_id, user)
    return Response(status_code=204)
