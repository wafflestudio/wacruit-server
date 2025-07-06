from typing import Annotated

from fastapi import Depends

from wacruit.src.apps.common.enums import RecruitingType
from wacruit.src.apps.common.exceptions import InvalidRecruitTypeException
from wacruit.src.apps.common.schemas import ListResponse
from wacruit.src.apps.portfolio.file.services import PortfolioFileService
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.problem.models import Problem
from wacruit.src.apps.problem.models import Testcase
from wacruit.src.apps.recruiting.exceptions import RecruitingNotAppliedException
from wacruit.src.apps.recruiting.exceptions import RecruitingNotFoundException
from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.recruiting.schemas import RecruitingCreateRequest
from wacruit.src.apps.recruiting.schemas import RecruitingInfoResponse
from wacruit.src.apps.recruiting.schemas import RecruitingResponse
from wacruit.src.apps.recruiting.schemas import RecruitingResultResponse
from wacruit.src.apps.recruiting.schemas import RecruitingSummaryResponse
from wacruit.src.apps.recruiting.schemas import RecruitingUpdateRequest
from wacruit.src.apps.recruiting.schemas import UserRecruitingResponse
from wacruit.src.apps.resume.models import ResumeQuestion
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
    ) -> UserRecruitingResponse:
        recruiting = (
            self.recruiting_repository.get_recruiting_with_code_submission_status_by_id(
                recruiting_id, user.id
            )
        )
        if recruiting is None:
            raise RecruitingNotFoundException()

        return UserRecruitingResponse.from_orm(recruiting)

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

    def cancel_recruiting(self, recruiting_id: int, user: User) -> None:
        self.user_service.remove_sensitive_information(user.id)
        self.portfolio_file_service.delete_all_portfolios(user.id)
        self.portfolio_url_service.delete_all_portfolio_urls(user.id, recruiting_id)
        self.resume_service.delete_all_resumes(user.id, recruiting_id)
        self.recruiting_repository.delete_recruiting_application(recruiting_id, user.id)

    def get_active_recruitings(self) -> ListResponse[RecruitingSummaryResponse]:
        recruitings = self.recruiting_repository.get_active_recruitings()
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

    def get_recruiting_info_by_type(
        self, recruiting_type: RecruitingType
    ) -> RecruitingInfoResponse | None:
        info = self.recruiting_repository.get_recruiting_info_by_type(recruiting_type)
        if not info:
            return None
        return RecruitingInfoResponse(**info.__dict__, type=recruiting_type.name)

    def create_recruiting(self, request: RecruitingCreateRequest) -> RecruitingResponse:
        if request.type not in RecruitingType.__members__:
            raise InvalidRecruitTypeException(request.type)

        recruiting = Recruiting(
            name=request.name,
            type=RecruitingType[request.type],
            generation=request.generation,
            is_active=request.is_active,
            from_date=request.from_date,
            to_date=request.to_date,
            short_description=request.short_description,
            description=request.description,
            resume_questions=[
                ResumeQuestion(**question.__dict__)
                for question in request.resume_questions
            ],
            problems=[
                Problem(
                    num=problem.num,
                    body=problem.body,
                    testcases=[
                        Testcase(**testcase.__dict__) for testcase in problem.testcases
                    ]
                    if problem.testcases
                    else None,
                )
                for problem in request.problems
            ]
            if request.problems
            else None,
        )
        recruiting = self.recruiting_repository.create_recruiting(recruiting)

        return RecruitingResponse.from_orm(recruiting)

    def update_recruiting(
        self, recruiting_id: int, request: RecruitingUpdateRequest
    ) -> RecruitingResponse:
        recruiting = self.recruiting_repository.get_recruiting_by_id(recruiting_id)
        if not recruiting:
            raise RecruitingNotFoundException()

        # 기본 필드들 업데이트
        for key, value in request.dict(
            exclude={"resume_questions", "problems"}
        ).items():
            if value is not None:
                setattr(recruiting, key, value)

        # resume_questions 업데이트
        if request.resume_questions is not None:
            # 이력서 질문 목록이 주어지면 기존 질문들을 모두 제거하고 새로 추가
            request.resume_questions.clear()
            recruiting.resume_questions = [
                ResumeQuestion(**question.dict())
                for question in request.resume_questions
            ]

        if request.problems is not None:
            # 문제 목록이 주어지면 기존 문제들을 모두 제거하고 새로 추가
            request.problems.clear()
            recruiting.problems = [
                Problem(**problem.dict()) for problem in request.problems
            ]

        updated_recruiting = self.recruiting_repository.update_recruiting(recruiting)

        return RecruitingResponse.from_orm(updated_recruiting)

    def get_recruitings_by_id(self, recruiting_id: int) -> RecruitingResponse:
        recruiting = self.recruiting_repository.get_recruiting_by_id(recruiting_id)
        if recruiting is None:
            raise RecruitingNotFoundException()

        return RecruitingResponse.from_orm(recruiting)
