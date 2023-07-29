from pydantic import EmailStr
import pytest

from wacruit.src.apps.recruiting.models import Recruiting
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.schemas import UserUpdateInvitationEmailsRequest
from wacruit.src.apps.user.services import UserService


def test_get_questions(
    resume_service: ResumeService,
    recruiting: Recruiting,
    resume_questions: list[ResumeQuestion],
):
    questions = resume_service.get_questions_by_recruiting_id(recruiting.id)
    assert len(questions) == len(resume_questions)
    for i, question in enumerate(questions):
        assert question.recruiting_id == resume_questions[i].recruiting_id
        assert question.question_num == resume_questions[i].question_num
        assert question.content_limit == resume_questions[i].content_limit
        assert question.content == resume_questions[i].content
        assert question.created_at is not None
        assert question.updated_at is not None


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


def test_update_resumes(
    user: User,
    resume_service: ResumeService,
    recruiting: Recruiting,
    resume_questions: list[ResumeQuestion],
):
    # user initially creates resume
    answers = list(
        f"Initial answer for question {i}" for i in range(len(resume_questions))
    )
    initial_resume_submissions = list(
        ResumeSubmissionCreateDto(
            question_id=question.id,
            answer=answer,
        )
        for question, answer in zip(resume_questions, answers)
    )
    resume_service.create_resume(
        user_id=user.id,
        recruiting_id=recruiting.id,
        resume_submissions=initial_resume_submissions,
    )

    # user updates their resume
    new_answers = list(
        f"Updated answer for question {i}" for i in range(len(resume_questions))
    )
    updated_resume_submissions = list(
        ResumeSubmissionCreateDto(
            question_id=question.id,
            answer=answer,
        )
        for question, answer in zip(resume_questions, new_answers)
    )
    updated_submissions = resume_service.update_resumes(
        user_id=user.id,
        recruiting_id=recruiting.id,
        resume_submissions=updated_resume_submissions,
    )
    assert len(updated_submissions) == len(new_answers)

    # retrieve the updated resumes and verify they match the new answers
    submissions_by_user_and_recruiting = (
        resume_service.get_resumes_by_user_and_recruiting_id(user.id, recruiting.id)
    )

    assert len(submissions_by_user_and_recruiting) == len(updated_submissions)
    for i, submission in enumerate(submissions_by_user_and_recruiting):
        assert submission.answer == new_answers[i]


def test_update_resumes_create_new_submission(
    user: User,
    resume_service: ResumeService,
    recruiting: Recruiting,
    resume_questions: list[ResumeQuestion],
):
    # user has not submitted any resume
    submissions_by_user_and_recruiting = (
        resume_service.get_resumes_by_user_and_recruiting_id(user.id, recruiting.id)
    )
    assert len(submissions_by_user_and_recruiting) == 0

    # user creates a new resume via update_resumes
    new_answers = list(f"Answer for question {i}" for i in range(len(resume_questions)))
    new_resume_submissions = list(
        ResumeSubmissionCreateDto(
            question_id=question.id,
            answer=answer,
        )
        for question, answer in zip(resume_questions, new_answers)
    )
    updated_submissions = resume_service.update_resumes(
        user_id=user.id,
        recruiting_id=recruiting.id,
        resume_submissions=new_resume_submissions,
    )

    assert len(updated_submissions) == len(new_answers)

    # retrieve the new resumes and verify they match the new answers
    submissions_by_user_and_recruiting = (
        resume_service.get_resumes_by_user_and_recruiting_id(user.id, recruiting.id)
    )

    assert len(submissions_by_user_and_recruiting) == len(updated_submissions)
    for i, submission in enumerate(submissions_by_user_and_recruiting):
        assert submission.answer == new_answers[i]
