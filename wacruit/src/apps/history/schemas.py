from typing import List

from pydantic import BaseModel

from wacruit.src.apps.common.schemas import OrmModel


class HistoryItemRequest(BaseModel):
    history_key: str
    history_value: str
    history_unit: str | None = None


class UpdateHistoryRequest(BaseModel):
    items: List[HistoryItemRequest]


class DeleteHistoryRequest(BaseModel):
    history_key: str


class HistoryResponse(OrmModel):
    id: int
    history_key: str
    history_value: str
    history_unit: str | None = None
