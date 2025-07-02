from sqlalchemy.orm import Mapped

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str255


class Seminar(DeclarativeBase):
    __tablename__ = "seminar"

    id: Mapped[intpk]
    title: Mapped[str30]
    content: Mapped[str255]
