from typing import Sequence

from fastapi import Depends
from sqlalchemy import and_
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from wacruit.src.apps.resume.exceptions import ResumeNotFound
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class ResumeRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def get_resumes_by_recruiting_id(self, recruiting_id) -> Sequence[ResumeSubmission]:
        query = (
            select(ResumeSubmission)
            .options(joinedload(ResumeSubmission.user))
            .where(ResumeSubmission.recruiting_id == recruiting_id)
        )
        return self.session.execute(query).scalars().all()

    def get_questions_by_recruiting_id(self, recruiting_id) -> Sequence[ResumeQuestion]:
        query = select(ResumeQuestion).where(
            ResumeQuestion.recruiting_id == recruiting_id
        )
        return self.session.execute(query).scalars().all()

    def get_resume_by_id(self, id: int) -> ResumeSubmission:
        query = select(ResumeSubmission).where(ResumeSubmission.id == id)
        try:
            return self.session.execute(query).scalar_one()
        except InvalidRequestError as exc:
            raise ResumeNotFound() from exc

    def get_resumes_by_user_recruiting_id(
        self, user_id: int, recruiting_id: int
    ) -> Sequence[ResumeSubmission]:
        query = (
            select(ResumeSubmission)
            .where(ResumeSubmission.user_id == user_id)
            .where(ResumeSubmission.recruiting_id == recruiting_id)
        )
        return self.session.execute(query).scalars().all()

    def create_resume_submission(
        self, resume_submission: ResumeSubmission
    ) -> ResumeSubmission:
        with self.transaction:
            self.session.add(resume_submission)
        return resume_submission

    def update_or_create_resume_submission(
        self, resume_submission: ResumeSubmission
    ) -> ResumeSubmission | None:
        filter_conditions = and_(
            ResumeSubmission.user_id == resume_submission.user_id,
            ResumeSubmission.recruiting_id == resume_submission.recruiting_id,
            ResumeSubmission.question_id == resume_submission.question_id,
        )
        select_stmt = select(ResumeSubmission).where(filter_conditions)
        update_stmt = (
            update(ResumeSubmission)
            .where(filter_conditions)
            .values(answer=resume_submission.answer)
        )
        with self.transaction:
            if self.session.execute(select_stmt).scalar():
                self.session.execute(update_stmt)
            else:
                self.session.add(resume_submission)
            return self.session.execute(select_stmt).scalar()

    def delete_resume_submission(self, id: int) -> None:
        with self.transaction:
            self.session.execute(
                delete(ResumeSubmission).where(ResumeSubmission.id == id)
            )

    def delete_resumes_by_user_recruiting_id(
        self, user_id: int, recruiting_id: int
    ) -> None:
        with self.transaction:
            self.session.execute(
                delete(ResumeSubmission)
                .where(ResumeSubmission.user_id == user_id)
                .where(ResumeSubmission.recruiting_id == recruiting_id)
            )
