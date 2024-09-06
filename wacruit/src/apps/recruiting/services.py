from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.portfolio.file.services import PortfolioFileService
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.recruiting.exceptions import RecruitingNotAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.recruiting.schemas import RecruitingResultResponse
from wacruit.src.apps.recruiting.schemas import RecruitingSummaryResponse
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.services import UserService


class RecruitingService:
    def __init__(
        self,
        portfolio_file_service: Annotated[PortfolioFileService, Depends()],
        portfolio_url_service: Annotated[PortfolioUrlService, Depends()],
        user_service: Annotated[UserService, Depends()],
        resume_service: Annotated[ResumeService, Depends()],
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
    ):
        self.portfolio_file_service = portfolio_file_service
        self.portfolio_url_service = portfolio_url_service
        self.user_service = user_service
        self.resume_service = resume_service
        self.recruiting_repository = recruiting_repository

    def get_all_recruiting(self) -> ListResponse[RecruitingSummaryResponse]:
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
                RecruitingSummaryResponse(
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

    def get_recruiting_result_by_id(
        self, recruiting_id: int, user: User
    ) -> RecruitingResultResponse:
        recruiting_result = self.recruiting_repository.get_recruiting_result_by_id(
            recruiting_id, user.id
        )
        if recruiting_result is None:
            raise RecruitingNotAppliedException()

        return RecruitingResultResponse(status=recruiting_result.status)

    def apply_recruiting(self, recruiting_id: int, user: User) -> None:
        self.recruiting_repository.create_recruiting_application(recruiting_id, user.id)

    async def cancel_recruiting(self, recruiting_id: int, user: User) -> None:
        await self.user_service.remove_sensitive_information(user.id)
        self.portfolio_file_service.delete_all_portfolios(user.id)
        self.portfolio_url_service.delete_all_portfolio_urls(user.id, recruiting_id)
        self.resume_service.delete_all_resumes(user.id, recruiting_id)
        self.recruiting_repository.delete_recruiting_application(recruiting_id, user.id)
