from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.enums import CodeSubmissionStatus
from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.schemas import RecruitingApplicantDto
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.user.models import User


class RecruitingService:
    def __init__(
        self,
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
    ):
        self.recruiting_repository = recruiting_repository

    def get_all_recruiting(self) -> ListResponse[RecruitingApplicantDto]:
        recruitings = self.recruiting_repository.get_all_recruitings()
        items = []
        for recruiting in recruitings:
            applicant_count = 0
            match recruiting.type:
                case RecruitingType.ROOKIE:
                    applicant_count = (
                        self.recruiting_repository.get_rookie_applicant_count(
                            recruiting.id
                        )
                    )
                case RecruitingType.DESIGNER:
                    applicant_count = 0  # 태양이가 해야되는 거
                case RecruitingType.PROGRAMMER:
                    raise NotImplementedError
            items.append(
                RecruitingApplicantDto(
                    **recruiting.__dict__, applicant_count=applicant_count
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
