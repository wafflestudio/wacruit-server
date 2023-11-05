from pydantic import BaseModel

from wacruit.src.apps.common.schemas import OrmModel


class PortfolioNameResponse(BaseModel):
    portfolio_name: str
    term: str | None = None


class PortfolioFileResponse(OrmModel):
    id: int
    file_name: str
    term: str | None = None


class PresignedUrlResponse(BaseModel):
    object_name: str
    presigned_url: str
    fields: dict[str, str] | None = None


class PortfolioRequest(BaseModel):
    term: str


class PortfolioFileRequest(BaseModel):
    term: str | None = None
    file_name: str | None = None
