from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.history.schemas import DeleteHistoryRequest
from wacruit.src.apps.history.schemas import HistoryResponse
from wacruit.src.apps.history.schemas import UpdateHistoryRequest
from wacruit.src.apps.history.services import HistoryService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/history", tags=["history"])


@v3_router.patch("")
def update_history(
    admin_user: AdminUser,
    history_service: Annotated[HistoryService, Depends()],
    update_request: UpdateHistoryRequest,
):
    updated_history_list = history_service.update_history(update_request)

    return [
        HistoryResponse.from_orm(updated_history)
        for updated_history in updated_history_list
    ]


@v3_router.get("")
def get_history(history_service: Annotated[HistoryService, Depends()]):
    history_list = history_service.get_history()

    return [HistoryResponse.from_orm(history) for history in history_list]


@v3_router.delete("", status_code=HTTPStatus.NO_CONTENT)
def delete_history(
    admin_user: AdminUser,
    history_service: Annotated[HistoryService, Depends()],
    delete_request: DeleteHistoryRequest,
):
    history_service.delete_history(delete_request)
