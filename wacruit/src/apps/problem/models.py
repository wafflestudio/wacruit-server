from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.recruiting.models import Recruiting
    from wacruit.src.apps.user.models import User


class Problem(DeclarativeBase):
    __tablename__ = "problem"
    __table_args__ = (UniqueConstraint("recruiting_id", "num"),)

    id: Mapped[intpk]
    recruiting_id: Mapped[int | None] = mapped_column(
        ForeignKey("recruiting.id", ondelete="SET NULL")
    )
    recruiting: Mapped["Recruiting"] = relationship(back_populates="problems")
    num: Mapped[int]  # recruiting 모델 추가 시 composite unique constraint 추가 예정
    body: Mapped[str] = mapped_column(Text)
    submissions: Mapped[list["CodeSubmission"]] = relationship(back_populates="problem")
    testcases: Mapped[list["TestCase"]] = relationship(back_populates="problem")


class CodeSubmission(DeclarativeBase):
    __tablename__ = "code_submission"

    id: Mapped[intpk]
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    user: Mapped["User"] = relationship(back_populates="code_submissions")
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problem.id", ondelete="SET NULL")
    )
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    tokens: Mapped[list["CodeSubmissionToken"]] = relationship(
        back_populates="submission"
    )
    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )


class CodeSubmissionToken(DeclarativeBase):
    __tablename__ = "code_submission_token"

    id: Mapped[intpk]
    token: Mapped[str255]
    submission_id: Mapped[int] = mapped_column(
        ForeignKey("code_submission.id", ondelete="CASCADE")
    )
    submission: Mapped["CodeSubmission"] = relationship(back_populates="tokens")


class TestCase(DeclarativeBase):
    __tablename__ = "testcase"

    id: Mapped[intpk]
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problem.id", ondelete="SET NULL")
    )
    problem: Mapped["Problem"] = relationship(back_populates="testcases")
    stdin: Mapped[str] = mapped_column(Text)
    expected_output: Mapped[str] = mapped_column(Text)
    time_limit: Mapped[float | None]
    is_example: Mapped[bool] = mapped_column(Boolean, default=False)
