from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.user.models import User


class Problem(DeclarativeBase):
    __tablename__ = "problem"

    id: Mapped[intpk]
    num: Mapped[int]
    body: Mapped[str] = mapped_column(Text, nullable=False)
    submissions: Mapped[list["CodeSubmission"]] = relationship(back_populates="problem")
    testcases: Mapped[list["TestCase"]] = relationship(back_populates="problem")


class CodeSubmission(DeclarativeBase):
    __tablename__ = "code_submission"

    id: Mapped[intpk]
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problem.id", ondelete="SET NULL")
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    )

    user: Mapped["User"] = relationship(back_populates="code_submissions")
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    results: Mapped[list["CodeSubmissionResult"]] = relationship(
        back_populates="submission"
    )


class CodeSubmissionResult(DeclarativeBase):
    __tablename__ = "code_submission_result"

    submission_id: Mapped[int] = mapped_column(
        ForeignKey("code_submission.id", ondelete="CASCADE"), primary_key=True
    )
    testcase_id: Mapped[int] = mapped_column(
        ForeignKey("testcase.id", ondelete="CASCADE"), primary_key=True
    )
    token: Mapped[str255]

    submission: Mapped["CodeSubmission"] = relationship(back_populates="results")
    testcase: Mapped["TestCase"] = relationship(back_populates="submission_results")


class TestCase(DeclarativeBase):
    __tablename__ = "testcase"

    id: Mapped[intpk]
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problem.id", ondelete="SET NULL")
    )
    problem: Mapped["Problem"] = relationship(back_populates="testcases")
    stdin: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_example: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    submission_results: Mapped[list["CodeSubmissionResult"]] = relationship(
        back_populates="testcase"
    )
