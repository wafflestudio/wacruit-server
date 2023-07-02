from typing import TYPE_CHECKING

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
    submissions: Mapped[list["CodeSubmission"]] = relationship(back_populates="problem")
    testcases: Mapped[list["TestCase"]] = relationship(back_populates="problem")


class CodeSubmission(DeclarativeBase):
    __tablename__ = "code_submission"

    id: Mapped[intpk]
    user: Mapped["User"] = relationship(back_populates="code_submissions")
    problem: Mapped["Problem"] = relationship(back_populates="submissions")
    token: Mapped[str] = mapped_column(String(255), nullable=False)


class TestCase(DeclarativeBase):
    __tablename__ = "testcase"

    id: Mapped[intpk]
    problem: Mapped["Problem"] = relationship(foreign_keys="problem.id")
    stdin: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[Text] = mapped_column(Text, nullable=False)
