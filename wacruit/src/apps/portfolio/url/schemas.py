from wacruit.src.apps.common.schemas import OrmModel
from wacruit.src.database.base import str255


class PortfolioUrlResponse(OrmModel):
    id: int
    url: str255
