from typing import Sequence

from fastapi import Depends

from wacruit.src.apps.resume.exceptions import ResumeNotFound
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.resume.repositories import ResumeRepository
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionWithUserDto
from wacruit.src.apps.user.models import User


class ResumeService:
    def __init__(self, resume_repository: ResumeRepository = Depends()) -> None:
        self.resume_repository = resume_repository

    def create_resume(
        self, user_id: int, request: Sequence[ResumeSubmissionCreateDto]
    ) -> list[ResumeSubmissionWithUserDto]:
        return [
            ResumeSubmissionWithUserDto.from_orm(
                self.resume_repository.create_resume_submission(
                    ResumeSubmission(user_id=user_id, **resume.dict())
                )
            )
            for resume in request
        ]

    def list_resumes(self, recruiting_id: int) -> list[ResumeSubmissionWithUserDto]:
        resumes = self.resume_repository.get_resumes(recruiting_id)
        return [ResumeSubmissionWithUserDto.from_orm(resume) for resume in resumes]

    def get_resumes(
        self, user_id: int, recruiting_id: int
    ) -> list[ResumeSubmissionWithUserDto]:
        resumes = self.resume_repository.get_resume(user_id, recruiting_id)
        return [ResumeSubmissionWithUserDto.from_orm(resume) for resume in resumes]

    def update_resumes(
        self, user_id: int, request: Sequence[ResumeSubmissionCreateDto]
    ) -> list[ResumeSubmissionWithUserDto]:
        resumes = [
            # TODO : get_resume_by_id를 호출하는 부분에서 쿼리 수정이 필요
            self.resume_repository.get_resume_by_id(1)
            for resume_info in request
        ]
        resume_dtos = []

        for i, resume_info in enumerate(request):
            if not resumes[i]:
                raise ResumeNotFound

            resume = resumes[i]
            resume.user_id = user_id
            resume.question_id = resume_info.question_id
            resume.recruiting_id = resume_info.recruiting_id
            resume.answer = resume_info.answer
            resume = self.resume_repository.update_resume_submission(resume)
            resume_dtos.append(ResumeSubmissionWithUserDto.from_orm(resume))

        return resume_dtos

    def delete_resume(self, id: int) -> None:
        self.resume_repository.delete_resume_submission(id)
