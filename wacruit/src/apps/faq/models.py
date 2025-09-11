from sqlalchemy.orm import Mapped

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255


class FAQ(DeclarativeBase):
    __tablename__ = "faq"

    id: Mapped[intpk]
    question: Mapped[str255]
    answer: Mapped[str255]
