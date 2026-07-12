from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import Query

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.pre_registration.schemas import CreatePreRegistrationRequest
from wacruit.src.apps.pre_registration.schemas import CreatePreRegistrationUserRequest
from wacruit.src.apps.pre_registration.schemas import PreRegistrationResponse
from wacruit.src.apps.pre_registration.schemas import PreRegistrationUserResponse
from wacruit.src.apps.pre_registration.schemas import SendPreRegistrationEmailRequest
from wacruit.src.apps.pre_registration.schemas import SendPreRegistrationEmailResponse
from wacruit.src.apps.pre_registration.schemas import UpdatePreRegistrationRequest
from wacruit.src.apps.pre_registration.services import PreRegistrationService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/pre-registration", tags=["preregistration"])


class PreRegistrationUserSearchParams:
    def __init__(
        self,
        active_only: bool = False,
        pre_registration_id: int | None = None,
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
    ) -> None:
        self.active_only = active_only
        self.pre_registration_id = pre_registration_id
        self.limit = limit
        self.offset = offset


@v3_router.get("/active", status_code=HTTPStatus.OK)
def get_active_pre_registration(
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
) -> PreRegistrationResponse:
    pre_registration = pre_registration_service.get_active_pre_registration()
    return PreRegistrationResponse.from_orm(pre_registration)


@v3_router.post("/users", status_code=HTTPStatus.CREATED)
def create_pre_registration_user(
    request: CreatePreRegistrationUserRequest,
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
) -> PreRegistrationUserResponse:
    return pre_registration_service.create_pre_registration_user(request)


@v3_router.post("/users/email", status_code=HTTPStatus.ACCEPTED)
def send_email_to_pre_registration_users(
    admin_user: AdminUser,
    request: SendPreRegistrationEmailRequest,
    background_tasks: BackgroundTasks,
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
) -> SendPreRegistrationEmailResponse:
    return pre_registration_service.send_email_to_pre_registration_users(
        request,
        background_tasks,
    )


@v3_router.get("/users", status_code=HTTPStatus.OK)
def get_pre_registration_users(
    admin_user: AdminUser,
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
    params: Annotated[PreRegistrationUserSearchParams, Depends()],
) -> ListResponse[PreRegistrationUserResponse]:
    pre_registration_users = pre_registration_service.get_pre_registration_users(
        pre_registration_id=params.pre_registration_id,
        active_only=params.active_only,
        limit=params.limit,
        offset=params.offset,
    )
    return ListResponse(items=pre_registration_users)


@v3_router.get("", status_code=HTTPStatus.OK)
def get_pre_registration(
    admin_user: AdminUser,
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
) -> ListResponse[PreRegistrationResponse]:
    pre_registration_list = pre_registration_service.get_pre_registration()
    return ListResponse(
        items=[PreRegistrationResponse.from_orm(item) for item in pre_registration_list]
    )


@v3_router.post("", status_code=HTTPStatus.CREATED)
def create_pre_registration(
    admin_user: AdminUser,
    request: CreatePreRegistrationRequest,
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
) -> PreRegistrationResponse:
    res = pre_registration_service.create_pre_registration(request)
    return PreRegistrationResponse.from_orm(res)


@v3_router.patch("/{pre_registration_id}", status_code=HTTPStatus.OK)
def update_pre_registration(
    admin_user: AdminUser,
    request: UpdatePreRegistrationRequest,
    pre_registration_id: int,
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
) -> PreRegistrationResponse:
    res = pre_registration_service.update_pre_registration(pre_registration_id, request)
    return PreRegistrationResponse.from_orm(res)


@v3_router.delete("/{pre_registration_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_pre_registration(
    admin_user: AdminUser,
    pre_registration_id: int,
    pre_registration_service: Annotated[PreRegistrationService, Depends()],
) -> None:
    pre_registration_service.delete_pre_registration(pre_registration_id)
