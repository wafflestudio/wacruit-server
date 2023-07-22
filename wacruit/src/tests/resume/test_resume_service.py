from pydantic import EmailStr
import pytest

from wacruit.src.apps.resume.exceptions import IncompleteResume
from wacruit.src.apps.resume.models import Recruiting
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.services import UserService


def test_create_resume(
    user: User,
    resume_service: ResumeService,
    recruiting: Recruiting,
    resume_questions: list[ResumeQuestion],
):
    answers = list(f"Answer for question {i}" for i in range(len(resume_questions)))
    resume_submissions = list(
        ResumeSubmissionCreateDto(
            question_id=question.id,
            answer=answer,
        )
        for question, answer in zip(resume_questions, answers)
    )
    submissions = resume_service.create_resume(
        user_id=user.id,
        recruiting_id=recruiting.id,
        resume_submissions=resume_submissions,
    )
    submissions_by_user_and_recruiting = (
        resume_service.get_resumes_by_user_and_recruiting_id(user.id, recruiting.id)
    )
    submissions_by_recruiting = resume_service.get_resumes_by_recruiting_id(
        recruiting.id
    )
    assert len(submissions) == len(answers)
    assert submissions == submissions_by_user_and_recruiting
    assert submissions == submissions_by_recruiting
    for i, submission in enumerate(submissions):
        assert submission.user_id == user.id
        assert submission.user.first_name == user.first_name
        assert submission.question_id == resume_questions[i].id
        assert submission.recruiting_id == recruiting.id
        assert submission.answer == answers[i]


def test_incomplete_resume(
    user: User,
    resume_service: ResumeService,
    recruiting: Recruiting,
    resume_questions: list[ResumeQuestion],
):
    # Answer for the last question is missing.
    answers = list(f"Answer for question {i}" for i in range(len(resume_questions) - 1))

    resume_submissions = list(
        ResumeSubmissionCreateDto(
            question_id=question.id,
            answer=answer,
        )
        for question, answer in zip(resume_questions, answers)
    )
    with pytest.raises(IncompleteResume):
        resume_service.create_resume(
            user_id=user.id,
            recruiting_id=recruiting.id,
            resume_submissions=resume_submissions,
        )
    submissions_by_user_and_recruiting = (
        resume_service.get_resumes_by_user_and_recruiting_id(user.id, recruiting.id)
    )
    assert len(submissions_by_user_and_recruiting) == 0


def test_withdraw_resume(
    user: User,
    resume_service: ResumeService,
    user_service: UserService,
    recruiting: Recruiting,
    resume_questions: list[ResumeQuestion],
):
    # user updated with university, github_email, slack_email
    user_service.update_invitaion_emails(
        user,
        UserUpdateInvitationEmailsRequest(
            github_email=EmailStr("github@email.com"),
        ),
    )

    # user submitted resume
    answers = list(f"Answer for question {i}" for i in range(len(resume_questions)))
    resume_submissions = list(
        ResumeSubmissionCreateDto(
            question_id=question.id,
            answer=answer,
        )
        for question, answer in zip(resume_questions, answers)
    )
    submissions = resume_service.create_resume(
        user_id=user.id,
        recruiting_id=recruiting.id,
        resume_submissions=resume_submissions,
    )
    assert len(submissions) == len(answers)

    # user withdraws resume
    resume_service.withdraw_resume(user.id, recruiting.id)
    submissions_by_user_and_recruiting = (
        resume_service.get_resumes_by_user_and_recruiting_id(user.id, recruiting.id)
    )
    assert len(submissions_by_user_and_recruiting) == 0

    user_from_db = user_service.user_repository.get_user_by_id(user.id)
    assert user_from_db is not None
    assert user_from_db.university is None
    assert user_from_db.github_email is None
    assert user_from_db.slack_email is None
