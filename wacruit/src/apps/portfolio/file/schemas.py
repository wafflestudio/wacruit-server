from pydantic import BaseModel

from wacruit.src.apps.common.schemas import OrmModel


class PortfolioNameResponse(BaseModel):
    portfolio_name: str


class PortfolioFileResponse(OrmModel):
    id: int
    file_name: str
    generation: int
    is_uploaded: bool = False


class PresignedUrlResponse(BaseModel):
    object_name: str
    presigned_url: str
    fields: dict[str, str]


class PresignedUrlWithIdResponse(BaseModel):
    object_name: str
    presigned_url: str
    fields: dict[str, str]
    portfolio_file_id: int


class PortfolioRequest(BaseModel):
    generation: int


class PortfolioFileRequest(BaseModel):
    generation: int
    file_name: str
