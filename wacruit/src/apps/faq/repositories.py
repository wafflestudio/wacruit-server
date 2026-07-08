from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import Session

from wacruit.src.apps.faq.models import FAQ
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction


class QuestionRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ) -> None:
        self.session = session
        self.transaction = transaction

    def get_question_by_id(self, questions_id: int) -> FAQ | None:
        return self.session.execute(
            select(FAQ).where(FAQ.id == questions_id)
        ).scalar_one_or_none()

    def get_questions(self) -> list[FAQ]:
        query = select(FAQ)
        return list(self.session.execute(query).scalars().all())

    def create_questions(self, question: FAQ) -> FAQ:
        with self.transaction:
            self.session.add(question)
        return question

    def update_question(self, question: FAQ) -> FAQ:
        with self.transaction:
            self.session.merge(question)
        return question

    def delete_question(self, questions_id: int) -> None:
        with self.transaction:
            self.session.execute(delete(FAQ).where(FAQ.id == questions_id))
