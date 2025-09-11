from sqlalchemy.orm import Mapped

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30
from wacruit.src.database.base import str255


class PreRegistration(DeclarativeBase):
    __tablename__ = "pre_registration"

    id: Mapped[intpk]
    url: Mapped[str255]
    generation: Mapped[str30]
    is_active: Mapped[bool]
