from pydantic import BaseModel


class PortfolioNameResponse(BaseModel):
    portfolio_name: str


class PresignedUrlResponse(BaseModel):
    object_name: str
    presigned_url: str
