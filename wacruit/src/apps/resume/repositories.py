from typing import Sequence

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import exc
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

    def get_resumes(self, recruiting_id) -> Sequence[ResumeSubmission]:
        query = (
            select(ResumeSubmission)
            .join(ResumeSubmission.user)
            .where(ResumeSubmission.recruiting_id == recruiting_id)
        )
        return self.session.execute(query).scalars().all()

    def get_resume_by_id(self, id: int) -> ResumeSubmission:
        query = select(ResumeSubmission).where(ResumeSubmission.id == id)
        return self.session.execute(query).scalar_one()

    def get_resume(
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

    def update_resume_submission(
        self, resume_submission: ResumeSubmission
    ) -> ResumeSubmission:
        with self.transaction:
            self.session.merge(resume_submission)
        return resume_submission

    def delete_resume_submission(self, id: int) -> None:
        with self.transaction:
            self.session.execute(
                delete(ResumeSubmission).where(ResumeSubmission.id == id)
            )
