from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.member.exceptions import MemberNotFoundException
from wacruit.src.apps.member.repositories import MemberRepository
from wacruit.src.apps.review.exceptions import ReviewNotFoundException
from wacruit.src.apps.review.models import Review
from wacruit.src.apps.review.repositories import ReviewRepository
from wacruit.src.apps.review.schemas import ReviewCreateRequest
from wacruit.src.apps.review.schemas import ReviewResponse
from wacruit.src.apps.review.schemas import ReviewUpdateRequest


class ReviewService:
    def __init__(
        self,
        member_repository: Annotated[MemberRepository, Depends()],
        review_repository: Annotated[ReviewRepository, Depends()],
    ):
        self.member_repository = member_repository
        self.review_repository = review_repository

    def create_review(self, request: ReviewCreateRequest):
        member = self.member_repository.get_member_by_id(request.member_id)
        if not member:
            raise MemberNotFoundException
        review = Review(
            title=request.title, content=request.content, member_id=member.id
        )
        return self.review_repository.create_review(review)

    def get_review(self, review_id: int):
        review = self.review_repository.get_review(review_id)
        if not review:
            raise ReviewNotFoundException
        writer = review.member

        return ReviewResponse(
            id=review.id,
            title=review.title,
            content=review.content,
            member_id=review.member_id,
            member_first_name=writer.first_name,
            member_last_name=writer.last_name,
            member_position=writer.position if writer.position else None,
            is_active=writer.is_active,
        )

    def get_reviews(
        self, offset: int = 0, limit: int = 20
    ) -> ListResponse[ReviewResponse]:
        reviews = self.review_repository.get_reviews(offset=offset, limit=limit)

        return ListResponse(
            items=[
                ReviewResponse(
                    id=review.id,
                    title=review.title,
                    content=review.content,
                    member_id=review.member_id,
                    member_first_name=review.member.first_name,
                    member_last_name=review.member.last_name,
                    member_position=review.member.position
                    if review.member.position
                    else None,
                    is_active=review.member.is_active,
                )
                for review in reviews
            ]
        )

    def update_review(
        self, review_id: int, request: ReviewUpdateRequest
    ) -> ReviewResponse:
        review = self.review_repository.get_review(review_id)
        if not review:
            raise ReviewNotFoundException

        if request.member_id:
            member_to_update = self.member_repository.get_member_by_id(
                request.member_id
            )
            if not member_to_update:
                raise MemberNotFoundException
            review.member_id = member_to_update.id

        if request.title:
            review.title = request.title

        if request.content:
            review.content = request.content

        updated_review = self.review_repository.update_review(review)

        return ReviewResponse(
            id=updated_review.id,
            title=updated_review.title,
            content=updated_review.content,
            member_id=updated_review.member_id,
            member_first_name=updated_review.member.first_name,
            member_last_name=updated_review.member.last_name,
            member_position=updated_review.member.position
            if updated_review.member.position
            else None,
            is_active=updated_review.member.is_active,
        )

    def delete_review(self, review_id: int):
        review = self.review_repository.get_review(review_id)
        if not review:
            raise ReviewNotFoundException

        self.review_repository.delete_review(review)
