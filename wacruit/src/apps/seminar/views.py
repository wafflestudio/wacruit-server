from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.seminar.schemas import CreateSeminarRequest
from wacruit.src.apps.seminar.schemas import SeminarResponse
from wacruit.src.apps.seminar.schemas import UpdateSeminarRequest
from wacruit.src.apps.seminar.services import SeminarService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/seminars", tags=["seminars"])


@v3_router.get("")
def get_seminars(
    admin_user: AdminUser, seminar_service: Annotated[SeminarService, Depends()]
) -> ListResponse:
    seminar_list = seminar_service.get_all_seminars()

    return ListResponse(
        items=[SeminarResponse.from_orm(seminar) for seminar in seminar_list]
    )


@v3_router.post("")
def create_seminar(
    admin_user: AdminUser,
    request: CreateSeminarRequest,
    seminar_service: Annotated[SeminarService, Depends()],
) -> SeminarResponse:
    created_seminar = seminar_service.create_seminar(request)
    return SeminarResponse.from_orm(created_seminar)


@v3_router.patch("/{seminar_id}")
def update_seminar(
    admin_user: AdminUser,
    seminar_id: int,
    request: UpdateSeminarRequest,
    seminar_service: Annotated[SeminarService, Depends()],
) -> SeminarResponse:
    updated_seminar = seminar_service.update_seminar(seminar_id, request)
    return SeminarResponse.from_orm(updated_seminar)


@v3_router.get("/active")
def get_active_seminar(
    seminar_service: Annotated[SeminarService, Depends()]
) -> ListResponse:
    seminar_list = seminar_service.get_active_seminar()

    return ListResponse(
        items=[SeminarResponse.from_orm(seminar) for seminar in seminar_list]
    )
