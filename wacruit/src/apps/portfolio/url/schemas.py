from pydantic import BaseModel

from wacruit.src.apps.common.schemas import OrmModel
from wacruit.src.database.base import str255


class PortfolioUrlResponse(OrmModel):
    id: int
    url: str255
    generation: int | None


class PortfolioUrlRequest(BaseModel):
    url: str255
    generation: int | None


class PortfolioRequest(BaseModel):
    generation: int
