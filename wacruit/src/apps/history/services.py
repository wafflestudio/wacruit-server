from datetime import datetime

from fastapi import Depends

from wacruit.src.apps.history.exceptions import HistoryNotFoundException
from wacruit.src.apps.history.models import History
from wacruit.src.apps.history.repositories import HistoryRepository
from wacruit.src.apps.history.schemas import DeleteHistoryRequest
from wacruit.src.apps.history.schemas import UpdateHistoryRequest


class HistoryService:
    def __init__(self, history_repository: HistoryRepository = Depends()):
        self.history_repository = history_repository

    def get_history(self) -> list[History]:
        history_list = self.history_repository.get_history()

        return history_list

    def update_history(self, update_request: UpdateHistoryRequest):
        to_update_list = []

        for item in update_request.items:
            to_update = History(
                history_key=item.history_key,
                history_value=item.history_value,
                history_unit=item.history_unit,
            )
            to_update_list.append(to_update)

        self.history_repository.update_history(to_update_list)

        return self.get_history()

    def delete_history(self, delete_request: DeleteHistoryRequest):
        result = self.history_repository.delete_history(delete_request.history_key)
        if not result:
            raise HistoryNotFoundException()
