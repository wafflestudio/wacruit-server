from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import text
from sqlalchemy import Text
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.apps.common.enums import CodeSubmissionResultStatus
from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import Language
from wacruit.src.apps.common.sql import CURRENT_TIMESTAMP
from wacruit.src.database.base import DeclarativeBase
from wacruit.src.database.base import intpk
from wacruit.src.database.base import str255

if TYPE_CHECKING:
    from wacruit.src.apps.recruiting.models import Recruiting
    from wacruit.src.apps.user.models import User


class Problem(DeclarativeBase):
    __tablename__ = "problem"

    id: Mapped[intpk]
    recruiting_id: Mapped[int | None] = mapped_column(
        ForeignKey("recruiting.id", ondelete="SET NULL")
    )
    num: Mapped[int]
    body: Mapped[str] = mapped_column(Text, nullable=False)

    recruiting: Mapped["Recruiting"] = relationship(back_populates="problems")
    submissions: Mapped[list["CodeSubmission"]] = relationship(back_populates="problem")
    testcases: Mapped[list["Testcase"]] = relationship(back_populates="problem")

    def __str__(self) -> str:
        return f"<Problem id={self.id}, num={self.num}, body={self.body[:10]}..>"


class CodeSubmission(DeclarativeBase):
    __tablename__ = "code_submission"

    id: Mapped[intpk]
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL")
    )
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problem.id", ondelete="SET NULL")
    )
    language: Mapped[Language]
    status: Mapped[CodeSubmissionStatus] = mapped_column(
        default=CodeSubmissionStatus.RUNNING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=CURRENT_TIMESTAMP,
    )
    source_code: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="code_submissions")
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    results: Mapped[list["CodeSubmissionResult"]] = relationship(
        back_populates="submission"
    )

    def __str__(self) -> str:
        return (
            f"<CodeSubmission id={self.id}, "
            f"user_id={self.user_id}, "
            f"problem_id={self.problem_id}>"
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
    status: Mapped[CodeSubmissionResultStatus] = mapped_column(
        default=CodeSubmissionResultStatus.RUNNING
    )
    time: Mapped[float | None] = mapped_column()
    memory: Mapped[int | None] = mapped_column()

    submission: Mapped["CodeSubmission"] = relationship(back_populates="results")
    testcase: Mapped["Testcase"] = relationship(back_populates="submission_results")


class Testcase(DeclarativeBase):
    __tablename__ = "testcase"

    id: Mapped[intpk]
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problem.id", ondelete="SET NULL")
    )
    stdin: Mapped[str] = mapped_column(MEDIUMTEXT, nullable=False)
    expected_output: Mapped[str] = mapped_column(MEDIUMTEXT, nullable=False)
    time_limit: Mapped[Decimal] = mapped_column(Numeric(10, 5))
    extra_time: Mapped[Decimal] = mapped_column(
        Numeric(10, 5), server_default=text("'0.00000'")
    )
    memory_limit: Mapped[int] = mapped_column(server_default=text("128000"))
    stack_limit: Mapped[int] = mapped_column(server_default=text("64000"))
    is_example: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    problem: Mapped["Problem"] = relationship(back_populates="testcases")
    submission_results: Mapped[list["CodeSubmissionResult"]] = relationship(
        back_populates="testcase", passive_deletes=True
    )

    def __str__(self) -> str:
        return (
            f"<Testcase id={self.id}, "
            f"problem_id={self.problem_id}, "
            f"is_example={self.is_example}>"
        )
