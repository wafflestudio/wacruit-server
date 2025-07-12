from sqlalchemy.orm import Session
from fastapi import Depends
from wacruit.src.database.connection import get_db_session
from wacruit.src.database.connection import Transaction
from wacruit.src.apps.review.models import Review

class ReviewRepository:
    def __init__(
        self,
        session: Session = Depends(get_db_session),
        transaction: Transaction = Depends(),
    ):
        self.session = session
        self.transaction = transaction

    def create_review(self, review: Review) -> Review:
        with self.transaction:
            self.session.add(review)
        return review

    def get_review(self, review_id: int) -> Review | None:
        return self.session.query(Review).filter(Review.id == review_id).first()

    def get_reviews(self, offset: int = 0, limit: int = 20) -> list[Review]:
        return self.session.query(Review).offset(offset).limit(limit).all()

    def update_review(self, updated_review: Review) -> Review:
        with self.transaction:
            self.session.merge(updated_review)
        return updated_review

    def delete_review(self, review: Review):
        with self.transaction:
            self.session.delete(review)