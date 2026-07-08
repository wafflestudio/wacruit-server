from typing import Annotated, Sequence

from fastapi import Depends

from wacruit.src.apps.portfolio.file.services_v2 import PortfolioFileService
from wacruit.src.apps.portfolio.url.services import PortfolioUrlService
from wacruit.src.apps.recruiting.exceptions import RecruitingClosedException
from wacruit.src.apps.recruiting.repositories import RecruitingRepository
from wacruit.src.apps.resume.exceptions import ResumeNotFound
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.resume.repositories import ResumeRepository
from wacruit.src.apps.resume.schemas import ResumeQuestionDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.schemas import UserResumeSubmissionDto
from wacruit.src.apps.user.services import UserService


class ResumeService:
    def __init__(
        self,
        resume_repository: Annotated[ResumeRepository, Depends()],
        recruiting_repository: Annotated[RecruitingRepository, Depends()],
        # portfolio_file_service: Annotated[PortfolioFileService, Depends()],
        # portfolio_url_service: Annotated[PortfolioUrlService, Depends()],
        user_service: Annotated[UserService, Depends()],
    ) -> None:
        self.resume_repository = resume_repository
        self.recruiting_repository = recruiting_repository
        # self.portfolio_file_service = portfolio_file_service
        # self.portfolio_url_service = portfolio_url_service
        self.user_service = user_service

    def get_questions_by_recruiting_id(
        self, recruiting_id: int
    ) -> list[ResumeQuestionDto]:
        questions = self.resume_repository.get_questions_by_recruiting_id(recruiting_id)
        return [ResumeQuestionDto.from_orm(question) for question in questions]

    def create_resume(
        self,
        user_id: int,
        recruiting_id: int,
        resume_submissions: Sequence[ResumeSubmissionCreateDto],
    ) -> list[UserResumeSubmissionDto]:
        recruiting = self.recruiting_repository.get_recruiting_by_id(recruiting_id)
        if recruiting is None or not recruiting.is_open:
            raise RecruitingClosedException()

        result = []
        for resume_submission_dto in resume_submissions:
            resume_submission = ResumeSubmission()
            resume_submission.user_id = user_id
            resume_submission.recruiting_id = recruiting_id
            resume_submission.question_id = resume_submission_dto.question_id
            resume_submission.answer = resume_submission_dto.answer
            saved_resume_submission = self.resume_repository.create_resume_submission(
                resume_submission
            )
            result.append(UserResumeSubmissionDto.from_orm(saved_resume_submission))

        return result

    def get_resumes_by_recruiting_id(
        self, recruiting_id: int
    ) -> list[UserResumeSubmissionDto]:
        resumes = self.resume_repository.get_resumes_by_recruiting_id(recruiting_id)
        return [UserResumeSubmissionDto.from_orm(resume) for resume in resumes]

    def get_resumes_by_user_and_recruiting_id(
        self, user_id: int, recruiting_id: int
    ) -> list[UserResumeSubmissionDto]:
        resumes = self.resume_repository.get_resumes_by_user_recruiting_id(
            user_id, recruiting_id
        )
        return [UserResumeSubmissionDto.from_orm(resume) for resume in resumes]

    def update_resumes(
        self,
        user_id: int,
        recruiting_id: int,
        resume_submissions: Sequence[ResumeSubmissionCreateDto],
    ) -> list[UserResumeSubmissionDto]:
        recruiting = self.recruiting_repository.get_recruiting_by_id(recruiting_id)
        if recruiting is None or not recruiting.is_open:
            raise RecruitingClosedException()

        resume_dtos = []

        for resume_info in resume_submissions:
            resume_submission = ResumeSubmission()
            resume_submission.user_id = user_id
            resume_submission.recruiting_id = recruiting_id
            resume_submission.question_id = resume_info.question_id
            resume_submission.answer = resume_info.answer
            updated_resume_submission = (
                self.resume_repository.update_or_create_resume_submission(
                    resume_submission
                )
            )
            if not updated_resume_submission:
                raise ResumeNotFound
            dto = UserResumeSubmissionDto.from_orm(updated_resume_submission)
            resume_dtos.append(dto)

        return resume_dtos

    def delete_resume(self, id: int) -> None:
        self.resume_repository.delete_resume_submission(id)

    def delete_all_resumes(self, user_id: int, recruiting_id: int) -> None:
        self.resume_repository.delete_resumes_by_user_recruiting_id(
            user_id, recruiting_id
        )

    # def withdraw_resume(self, user_id: int, recruiting_id: int) -> None:
    #     self.user_service.remove_sensitive_information(user_id)
    #     self.portfolio_file_service.delete_all_portfolios(user_id)
    #     self.portfolio_url_service.delete_all_portfolio_urls(user_id, recruiting_id)
    #     self.resume_repository.delete_resumes_by_user_recruiting_id(
    #         user_id, recruiting_id
    #     )
