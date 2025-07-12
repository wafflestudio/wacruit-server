from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.review.schemas import ReviewCreateRequest
from wacruit.src.apps.review.schemas import ReviewResponse
from wacruit.src.apps.review.schemas import ReviewUpdateRequest
from wacruit.src.apps.review.services import ReviewService
from wacruit.src.apps.user.dependencies import AdminUser

v3_router = APIRouter(prefix="/v3/reviews", tags=["reviews"])


@v3_router.post("")
def create_review(
    admin_user: AdminUser,
    request: ReviewCreateRequest,
    review_service: Annotated[ReviewService, Depends()],
):
    return review_service.create_review(request)


@v3_router.get("/{review_id}")
def get_review(
    review_id: int,
    review_service: Annotated[ReviewService, Depends()],
) -> ReviewResponse:
    return review_service.get_review(review_id)


@v3_router.get("")
def get_reviews(
    review_service: Annotated[ReviewService, Depends()],
    offset: int = 0,
    limit: int = 20,
) -> ListResponse[ReviewResponse]:
    return review_service.get_reviews(offset=offset, limit=limit)


@v3_router.patch("/{review_id}")
def update_review(
    admin_user: AdminUser,
    review_id: int,
    request: ReviewUpdateRequest,
    review_service: Annotated[ReviewService, Depends()],
) -> ReviewResponse:
    return review_service.update_review(review_id, request)


@v3_router.delete("/{review_id}")
def delete_review(
    admin_user: AdminUser,
    review_id: int,
    review_service: Annotated[ReviewService, Depends()],
):
    return review_service.delete_review(review_id)
