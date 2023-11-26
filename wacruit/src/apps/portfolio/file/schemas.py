from pydantic import BaseModel

from wacruit.src.apps.common.schemas import OrmModel


class PortfolioNameResponse(BaseModel):
    portfolio_name: str
    generation: str | None = None


class PortfolioFileResponse(OrmModel):
    id: int
    file_name: str
    generation: int | None = None
    is_uploaded: bool = False


class PresignedUrlResponse(BaseModel):
    object_name: str
    presigned_url: str
    fields: dict[str, str] | None = None
    portfolio_file_id: int | None = None


class PortfolioRequest(BaseModel):
    generation: int


class PortfolioFileRequest(BaseModel):
    generation: int | None = None
    file_name: str | None = None
