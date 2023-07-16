from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30

if TYPE_CHECKING:
    from wacruit.src.apps.problem.models import Problem


class Recruiting(DeclarativeBase):
    __tablename__ = "recruiting"

    id: Mapped[intpk]
    name: Mapped[str30]
    is_active: Mapped[bool]
    from_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    to_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    # resume_submissions: Mapped[list["ResumeSubmission"]] = relationship(
    #     back_populates="recruiting"
    # )
    # resume_questions: Mapped[list["ResumeQuestion"]] = relationship(
    #     back_populates="recruiting"
    # )
    problems: Mapped[list["Problem"]] = relationship(back_populates="recruiting")

    description: Mapped[str | None] = mapped_column(String(10000))
