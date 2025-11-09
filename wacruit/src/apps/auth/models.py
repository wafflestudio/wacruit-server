from sqlalchemy.orm import Mapped

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255


class BlockedToken(DeclarativeBase):
    __tablename__ = "blocked_token"

    id: Mapped[intpk]
    token: Mapped[str255]
