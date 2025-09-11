from pydantic import BaseModel

from wacruit.src.apps.common.schemas import OrmModel


class UpdateHistoryRequest(BaseModel):
    class Config:
        extra = "allow"


class HistoryResponse(OrmModel):
    id: int
    history_key: str
    history_value: str
