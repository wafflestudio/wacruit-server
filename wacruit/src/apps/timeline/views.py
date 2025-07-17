from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.enums import TimelineGroupType
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.timeline.schemas import TimelineCategoryCreateUpdateRequest
from wacruit.src.apps.timeline.schemas import TimelineCategoryResponse
from wacruit.src.apps.timeline.schemas import TimelineCreateRequest
from wacruit.src.apps.timeline.schemas import TimelineResponse
from wacruit.src.apps.timeline.schemas import TimelineUpdateRequest
from wacruit.src.apps.timeline.services import TimelineService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/timelines", tags=["timelines"])


@v3_router.post("/categories", status_code=HTTPStatus.OK)
def create_timeline_category(
    admin_user: AdminUser,
    request: TimelineCategoryCreateUpdateRequest,
    timeline_service: Annotated[TimelineService, Depends()],
) -> TimelineCategoryResponse:
    return timeline_service.create_category(request)


@v3_router.get("/categories")
def get_all_timeline_categories(
    admin_user: AdminUser,
    timeline_service: Annotated[TimelineService, Depends()],
    group: TimelineGroupType | None = None,
) -> ListResponse[TimelineCategoryResponse]:
    return timeline_service.get_all_categories(group=group)


@v3_router.patch("/categories/{category_id}")
def update_timeline_category(
    admin_user: AdminUser,
    category_id: int,
    request: TimelineCategoryCreateUpdateRequest,
    timeline_service: Annotated[TimelineService, Depends()],
) -> TimelineCategoryResponse:
    return timeline_service.update_category(category_id, request)


@v3_router.delete("/categories/{category_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_timeline_category(
    admin_user: AdminUser,
    category_id: int,
    timeline_service: Annotated[TimelineService, Depends()],
):
    timeline_service.delete_category(category_id)


@v3_router.post("", status_code=HTTPStatus.CREATED)
def create_timeline(
    admin_user: AdminUser,
    request: TimelineCreateRequest,
    timeline_service: Annotated[TimelineService, Depends()],
) -> TimelineResponse:
    return timeline_service.create_timeline(request)


@v3_router.get("")
def get_all_timelines(
    timeline_service: Annotated[TimelineService, Depends()],
    group: TimelineGroupType | None = None,
) -> ListResponse[TimelineResponse]:
    return timeline_service.get_all_timelines(group=group)


@v3_router.patch("/{timeline_id}")
def update_timeline(
    admin_user: AdminUser,
    timeline_id: int,
    request: TimelineUpdateRequest,
    timeline_service: Annotated[TimelineService, Depends()],
) -> TimelineResponse:
    return timeline_service.update_timeline(timeline_id, request)


@v3_router.delete("/{timeline_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_timeline(
    admin_user: AdminUser,
    timeline_id: int,
    timeline_service: Annotated[TimelineService, Depends()],
):
    timeline_service.delete_timeline(timeline_id)
