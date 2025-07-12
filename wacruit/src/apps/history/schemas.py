from pydantic import BaseModel


class UpdateHistoryRequest(BaseModel):
    class Config:
        extra = "allow"


class HistoryResponse(BaseModel):
    __root__: dict[str, str]
