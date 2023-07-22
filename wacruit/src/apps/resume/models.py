from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP
from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP_ON_UPDATE
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk

if TYPE_CHECKING:
    from wacruit.src.apps.recruiting.models import Recruiting
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
        server_default=CURRENT_TIMESTAMP,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP_ON_UPDATE,
    )
