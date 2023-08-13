from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.portfolio.file.services import PortfolioFileService
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.schemas import RecruitingApplicantDto
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.user.models import User


class RecruitingService:
    def __init__(
        self,
        portfolio_file_service: Annotated[PortfolioFileService, Depends()],
        portfolio_url_service: Annotated[PortfolioUrlService, Depends()],
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
    ):
        self.portfolio_file_service = portfolio_file_service
        self.portfolio_url_service = portfolio_url_service
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
                    file_applicant_user_ids = (
                        self.portfolio_file_service.get_all_applicant_user_ids()
                    )
                    url_applicant_user_ids = (
                        self.portfolio_url_service.get_all_applicant_user_ids()
                    )
                    applicant_count = len(
                        set(file_applicant_user_ids + url_applicant_user_ids)
                    )
                case RecruitingType.PROGRAMMER:
                    # Not implemented
                    applicant_count = -1
            items.append(
                RecruitingApplicantDto(
                    **recruiting.__dict__, applicant_count=applicant_count
                )
            )
        return ListResponse(items=items)

    def get_recruiting_by_id(
        self, recruiting_id: int, user: User
    ) -> RecruitingResponse:
        recruiting = (
            self.recruiting_repository.get_recruiting_with_code_submission_status_by_id(
                recruiting_id, user.id
            )
        )
        if recruiting is None:
            raise RecruitingNotFoundException()

        return RecruitingResponse.from_orm(recruiting)
