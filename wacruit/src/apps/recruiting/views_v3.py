from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.schemas import RecruitingCreateRequest
from wacruit.src.apps.recruiting.schemas import RecruitingInfoResponse
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.recruiting.schemas import RecruitingSummaryResponse
from wacruit.src.apps.recruiting.schemas import RecruitingUpdateRequest
from wacruit.src.apps.recruiting.services import RecruitingService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/recruitings", tags=["recruitings"])


@v3_router.post("/")
def create_recruiting(
    admin_user: AdminUser,
    recruiting_service: Annotated[RecruitingService, Depends()],
    request: RecruitingCreateRequest,
) -> RecruitingResponse:
    return recruiting_service.create_recruiting(request)


@v3_router.get("/active")
def get_active_recruitings(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingSummaryResponse]:
    return recruiting_service.get_active_recruitings()


@v3_router.get("/by-type")
def get_recruitings_by_type(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingInfoResponse]:
    items = []
    for recruiting_type in RecruitingType.__members__.values():
        result = recruiting_service.get_recruiting_info_by_type(recruiting_type)
        if result is not None:
            items.append(result)
    return ListResponse(items=items)


@v3_router.patch("/{recruiting_id}")
def update_recruiting(
    admin_user: AdminUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
    request: RecruitingUpdateRequest,
) -> RecruitingResponse:
    return recruiting_service.update_recruiting(recruiting_id, request)


@v3_router.get("/{recruiting_id}")
def get_recruiting_by_id(
    admin_user: AdminUser,
    recruiting_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> RecruitingResponse:
    return recruiting_service.get_recruiting_by_id(recruiting_id)
