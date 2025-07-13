from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.history.schemas import HistoryResponse
from wacruit.src.apps.history.schemas import UpdateHistoryRequest
from wacruit.src.apps.history.services import HistoryService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/history", tags=["history"])


@v3_router.patch("/")
def update_history(
    admin_user: AdminUser,
    history_service: Annotated[HistoryService, Depends()],
    update_request: UpdateHistoryRequest,
):
    updated_history = history_service.update_history(update_request)
    response_dict = {}
    for h in updated_history:
        response_dict[h.history_key] = h.history_value

    return HistoryResponse(__root__=response_dict)


@v3_router.get("/")
def get_history(history_service: Annotated[HistoryService, Depends()]):
    history_list = history_service.get_history()
    response_dict = {}
    for h in history_list:
        response_dict[h.history_key] = h.history_value

    return HistoryResponse(__root__=response_dict)
