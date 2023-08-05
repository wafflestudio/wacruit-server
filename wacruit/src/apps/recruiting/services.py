from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.schemas import RecruitingApplicantDto
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.services import UserService


class RecruitingService:
    def __init__(
        self,
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
        user_service: Annotated[UserService, Depends()],
    ):
        self.recruiting_repository = recruiting_repository
        self.user_service = user_service

    def get_all_recruiting(self) -> ListResponse[RecruitingApplicantDto]:
        recruitings = self.recruiting_repository.get_all_recruitings()
        user_count = self.user_service.get_user_count()
        items = []
        for recruiting in recruitings:
            items.append(
                RecruitingApplicantDto(
                    **recruiting.__dict__, applicant_count=user_count
                )
            )
        return ListResponse(items=items)

    def get_recruiting_by_id(
        self, recruiting_id: int, user: User
    ) -> RecruitingResponse:
        recruiting = self.recruiting_repository.get_recruiting_by_id(
            recruiting_id, user.id
        )
        if recruiting is None:
            raise RecruitingNotFoundException()

        return RecruitingResponse.from_orm(recruiting)
