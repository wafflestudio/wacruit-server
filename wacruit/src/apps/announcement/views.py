from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from wacruit.src.apps.announcement.exceptions import AnnouncementNotFound
from wacruit.src.apps.announcement.schemas import AnnouncementCreateDto
from wacruit.src.apps.announcement.schemas import AnnouncementDto
from wacruit.src.apps.announcement.services import AnnouncementService
from wacruit.src.apps.common.exceptions import responses_from
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.user.dependencies import AdminUser

v1_router = APIRouter(prefix="/v1/announcements", tags=["announcements"])


@v1_router.get("/")
async def list_announcements(
    announcement_service: AnnouncementService = Depends(),
) -> ListResponse[AnnouncementDto]:
    announcements = announcement_service.list_announcements()
    return ListResponse(items=announcements)


@v1_router.post("/")
async def create_announcement(
    user: AdminUser,
    request: AnnouncementCreateDto,
    announcement_service: AnnouncementService = Depends(),
) -> AnnouncementDto:
    return announcement_service.create_announcement(request)


@v1_router.put("/{id}", responses=responses_from(AnnouncementNotFound))
async def update_announcement(
    id: int,
    user: AdminUser,
    request: AnnouncementCreateDto,
    announcement_service: AnnouncementService = Depends(),
) -> AnnouncementDto:
    return announcement_service.update_announcement(id, request)


@v1_router.delete(
    "/{id}", responses=responses_from(AnnouncementNotFound), status_code=204
)
async def delete_announcement(
    id: int,
    user: AdminUser,
    announcement_service: AnnouncementService = Depends(),
):
    announcement_service.delete_announcement(id)
    return Response(status_code=204)
