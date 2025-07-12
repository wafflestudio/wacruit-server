from datetime import datetime

from fastapi import Depends

from wacruit.src.apps.history.exceptions import HistoryEmptyException
from wacruit.src.apps.history.models import History
from wacruit.src.apps.history.repositories import HistoryRepository
from wacruit.src.apps.history.schemas import UpdateHistoryRequest


class HistoryService:
    def __init__(self, history_repository: HistoryRepository = Depends()):
        self.history_repository = history_repository

    def get_history(self) -> list[History]:
        history_list = self.history_repository.get_history()
        operation_period = self.calculate_operation_period()

        if operation_period is not None:
            history_list.append(
                History(
                    history_key="operation_period", history_value=str(operation_period)
                )
            )

        if not history_list:
            raise HistoryEmptyException
        return history_list

    def update_history(self, update_request: UpdateHistoryRequest):
        req = update_request.dict()

        for k, v in req.items():
            to_update = History(history_key=k, history_value=v)
            self.history_repository.update_history(to_update)

        return self.get_history()

    def calculate_operation_period(self) -> int | None:
        start_date = self.history_repository.get_start_date()
        now = datetime.now()

        if start_date is None:
            return None
        return now.year - start_date.year
