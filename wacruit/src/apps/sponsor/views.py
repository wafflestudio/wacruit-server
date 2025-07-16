from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.sponsor.schemas import SponsorBriefResponse
from wacruit.src.apps.sponsor.schemas import SponsorCreateRequest
from wacruit.src.apps.sponsor.schemas import SponsorInfoResponse
from wacruit.src.apps.sponsor.schemas import SponsorUpdateRequest
from wacruit.src.apps.sponsor.services import SponsorService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/sponsor", tags=["sponsor"])


@v3_router.post("")
def create_sponsor(
    admin_user: AdminUser,
    request: SponsorCreateRequest,
    sponsor_service: Annotated[SponsorService, Depends()],
) -> Response:
    sponsor_service.create_sponsor(request)

    return Response(status_code=201)


@v3_router.get("/{sponsor_id}")
def get_sponsor(
    sponsor_id: str,
    sponsor_service: Annotated[SponsorService, Depends()],
) -> SponsorInfoResponse:
    return sponsor_service.get_sponsor_by_id(sponsor_id)


@v3_router.get("")
def get_all_sponsors(
    sponsor_service: Annotated[SponsorService, Depends()],
) -> ListResponse[SponsorBriefResponse]:
    return sponsor_service.get_all_sponsors()


@v3_router.patch("/{sponsor_id}")
def update_sponsor(
    admin_user: AdminUser,
    sponsor_id: str,
    request: SponsorUpdateRequest,
    sponsor_service: Annotated[SponsorService, Depends()],
) -> SponsorInfoResponse:
    return sponsor_service.update_sponsor(sponsor_id, request)
