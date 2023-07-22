from wacruit.src.apps.resume.models import Recruiting
from wacruit.src.apps.resume.models import ResumeQuestion
from wacruit.src.apps.resume.models import ResumeSubmission
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.apps.user.models import User


def test_create_resume(
    user: User,
    resume_service: ResumeService,
    resume_question: ResumeQuestion,
    recruiting: Recruiting,
):
    answers = ["answer1", "answer2", "answer3"]
    resume_submissions = list(
        ResumeSubmissionCreateDto(
            question_id=resume_question.id,
            recruiting_id=recruiting.id,
            answer=answer,
        )
        for answer in answers
    )
    submissions = resume_service.create_resume(
        user.id, resume_submissions=resume_submissions
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
        assert submission.question_id == resume_question.id
        assert submission.recruiting_id == recruiting.id
        assert submission.answer == answers[i]
