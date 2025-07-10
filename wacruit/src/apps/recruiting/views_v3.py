from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.schemas import RecruitingCreateRequest
from wacruit.src.apps.recruiting.schemas import RecruitingInfoCreateRequest
from wacruit.src.apps.recruiting.schemas import RecruitingInfoResponse
from wacruit.src.apps.recruiting.schemas import RecruitingInfoUpdateRequest
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


@v3_router.get("/info/{recruiting_type}")
def get_recruitings_by_type(
    recruiting_type: RecruitingType,
    recruiting_service: Annotated[RecruitingService, Depends()],
) -> ListResponse[RecruitingInfoResponse]:
    result = recruiting_service.get_recruiting_infos_by_type(recruiting_type)
    if result is not None:
        return result
    return ListResponse(items=[])


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


@v3_router.post("/info")
def create_recruiting_info(
    admin_user: AdminUser,
    recruiting_service: Annotated[RecruitingService, Depends()],
    request: RecruitingInfoCreateRequest,
) -> RecruitingInfoResponse:
    return recruiting_service.create_recruiting_info(request)


@v3_router.patch("/info/{recruiting_info_id}")
def update_recruiting_info(
    admin_user: AdminUser,
    recruiting_info_id: int,
    recruiting_service: Annotated[RecruitingService, Depends()],
    request: RecruitingInfoUpdateRequest,
) -> RecruitingInfoResponse:
    return recruiting_service.update_recruiting_info(recruiting_info_id, request)
