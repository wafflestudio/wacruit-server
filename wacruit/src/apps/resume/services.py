from typing import Sequence

from fastapi import Depends

from wacruit.src.apps.resume.exceptions import ResumeNotFound
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.resume.repositories import ResumeRepository
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionDto
from wacruit.src.apps.resume.schemas import ResumeSubmissionWithUserDto


class ResumeService:
    def __init__(self, resume_repository: ResumeRepository = Depends()) -> None:
        self.resume_repository = resume_repository

    def create_resume(
        self, request: Sequence[ResumeSubmissionCreateDto]
    ) -> list[ResumeSubmissionWithUserDto]:
        return [
            ResumeSubmissionWithUserDto.from_orm(
                self.resume_repository.create_resume_submission(
                    ResumeSubmission(**resume.dict())
                )
            )
            for resume in request
        ]

    def list_resumes(self, recruiting_id: int) -> list[ResumeSubmissionWithUserDto]:
        resumes = self.resume_repository.get_resumes(recruiting_id)
        return [ResumeSubmissionWithUserDto.from_orm(resume) for resume in resumes]

    def get_resume(
        self, request: ResumeSubmissionCreateDto
    ) -> ResumeSubmissionWithUserDto:
        resume = self.resume_repository.get_resume(
            request.user_id, request.recruiting_id
        )
        if resume is None:
            raise ResumeNotFound
        return ResumeSubmissionWithUserDto.from_orm(resume)

    def update_resumes(
        self, request: Sequence[ResumeSubmissionDto]
    ) -> list[ResumeSubmissionWithUserDto]:
        resumes = [
            self.resume_repository.get_resume_by_id(resume_info.id)
            for resume_info in request
        ]
        resume_dtos = []

        for i, resume_info in enumerate(request):
            if not resumes[i]:
                raise ResumeNotFound

            resume = resumes[i]
            resume.user_id = resume_info.user_id
            resume.question_id = resume_info.question_id
            resume.recruiting_id = resume_info.recruiting_id
            resume.answer = resume_info.answer
            resume = self.resume_repository.update_resume_submission(resume)
            resume_dtos.append(ResumeSubmissionWithUserDto.from_orm(resume))

        return resume_dtos

    def delete_resume(self, id: int) -> None:
        self.resume_repository.delete_resume_submission(id)
