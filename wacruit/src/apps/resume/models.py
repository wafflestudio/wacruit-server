from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30

if TYPE_CHECKING:
    from wacruit.src.apps.user.models import User


class ResumeQuestion(DeclarativeBase):
    __tablename__ = "resume_question"

    id: Mapped[intpk]
    recruiting_id: Mapped[int | None] = mapped_column(
        ForeignKey("recruiting.id", ondelete="SET NULL")
    )
    recruiting: Mapped["Recruiting"] = relationship(back_populates="resume_questions")
    resume_submissions: Mapped[list["ResumeSubmission"]] = relationship(
        back_populates="question"
    )
    question_num: Mapped[int]
    content_limit: Mapped[int]
    content: Mapped[str | None] = mapped_column(String(10000))


class ResumeSubmission(DeclarativeBase):
    __tablename__ = "resume_submission"

    id: Mapped[intpk]
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    user: Mapped["User"] = relationship(back_populates="resume_submissions")
    question_id: Mapped[int | None] = mapped_column(
        ForeignKey("resume_question.id", ondelete="SET NULL")
    )
    question: Mapped["ResumeQuestion"] = relationship(
        back_populates="resume_submissions"
    )
    recruiting_id: Mapped[int | None] = mapped_column(
        ForeignKey("recruiting.id", ondelete="SET NULL")
    )
    recruiting: Mapped["Recruiting"] = relationship(back_populates="resume_submissions")
    answer: Mapped[str | None] = mapped_column(String(10000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),  # pylint: disable=not-callable
        server_default=func.now(),  # pylint: disable=not-callable
    )


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
    resume_submissions: Mapped[list["ResumeSubmission"]] = relationship(
        back_populates="recruiting"
    )
    resume_questions: Mapped[list["ResumeQuestion"]] = relationship(
        back_populates="recruiting"
    )

    description: Mapped[str | None] = mapped_column(String(10000))
