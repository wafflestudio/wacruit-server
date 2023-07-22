from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.schemas import RecruitingListResponse
from wacruit.src.apps.recruiting.services import RecruitingService

v1_router = APIRouter(prefix="/v1/recruiting", tags=["problem"])


@v1_router.get("")
def get_recruitings(
    recruiting_service: Annotated[RecruitingService, Depends()]
) -> ListResponse[RecruitingListResponse]:
    return recruiting_service.get_all_recruiting()
