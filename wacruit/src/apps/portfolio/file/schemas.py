from pydantic import BaseModel


class PortfolioNameResponse(BaseModel):
    portfolio_name: str


class PresignedUrlResponse(BaseModel):
    object_name: str
    presigned_url: str
    fields: dict[str, str] | None = None


class PortfolioRequest(BaseModel):
    term: str

class PortfolioFileRequest(BaseModel):
    term: str
    file_name: str
