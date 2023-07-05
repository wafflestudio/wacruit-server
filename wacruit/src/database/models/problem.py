from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from wacruit.src.database.models.base import DeclarativeBase
from wacruit.src.database.models.base import intpk

if TYPE_CHECKING:
    from wacruit.src.database.models import User


class Problem(DeclarativeBase):
    __tablename__ = "problem"

    id: Mapped[intpk]
    body: Mapped[str] = mapped_column(Text, nullable=False)
    submissions: Mapped[list["CodeSubmission"]] = relationship(
        back_populates="problem", cascade="all, delete"
    )
    testcases: Mapped[list["TestCase"]] = relationship(
        back_populates="problem", cascade="all, delete"
    )


class CodeSubmission(DeclarativeBase):
    __tablename__ = "code_submission"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="code_submissions")
    problem_id: Mapped[int] = mapped_column(ForeignKey("problem.id"))
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    token: Mapped[str] = mapped_column(String(255), nullable=False)


class TestCase(DeclarativeBase):
    __tablename__ = "testcase"

    id: Mapped[intpk]
    problem_id: Mapped[int] = mapped_column(ForeignKey("problem.id"))
    problem: Mapped["Problem"] = relationship(back_populates="testcases")
    stdin: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[Text] = mapped_column(Text, nullable=False)
    is_example: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
