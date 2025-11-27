from sqlalchemy.orm import Mapped

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str50


class History(DeclarativeBase):
    __tablename__ = "history"

    id: Mapped[intpk]
    history_key: Mapped[str50]
    history_value: Mapped[str50]
    history_unit: Mapped[str50]
