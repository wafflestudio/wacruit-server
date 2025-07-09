from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from wacruit.src.apps.common.enums import SeminarType
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk


class Seminar(DeclarativeBase):
    __tablename__ = "seminar"

    id: Mapped[intpk]
    seminar_type: Mapped[SeminarType]
    curriculum_info: Mapped[str] = mapped_column(Text)
    prerequisite_info: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool]
