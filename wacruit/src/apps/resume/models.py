from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.user.models import User
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str30


class ResumeQuestion(DeclarativeBase):
    __tablename__ = "resume_question"

    id: Mapped[intpk]
    recruiting_id: Mapped[int] = mapped_column(
        ForeignKey("recruiting.id", ondelete="CASCADE")
    )
    recruiting: Mapped["Recruiting"] = relationship(
        "Recruiting", back_populates="resume_questions"
    )
    resume_submissions: Mapped[list["ResumeSubmission"]] = relationship(
        back_populates="question"
    )
    question_num: Mapped[int]
    content: Mapped[str | None] = mapped_column(String(10000))


class ResumeSubmission(DeclarativeBase):
    __tablename__ = "resume_submission"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User", back_populates="resume_submissions")
    question_id: Mapped[int] = mapped_column(
        ForeignKey("resume_question.id", ondelete="CASCADE")
    )
    question: Mapped["ResumeQuestion"] = relationship(
        "ResumeQuestion", back_populates="resume_submissions"
    )
    recruiting_id: Mapped[int] = mapped_column(
        ForeignKey("recruiting.id", ondelete="CASCADE")
    )
    recruiting: Mapped["Recruiting"] = relationship(
        "Recruiting", back_populates="resume_submissions"
    )
    answer: Mapped[str | None] = mapped_column(String(10000))


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
