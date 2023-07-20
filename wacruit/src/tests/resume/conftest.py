import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.resume.repositories import ResumeRepository
from wacruit.src.apps.resume.schemas import ResumeSubmissionCreateDto
from wacruit.src.apps.resume.services import ResumeService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def resume_repository(db_session: Session):
    return ResumeRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def resume_service(resume_repository: ResumeRepository):
    return ResumeService(resume_repository=resume_repository)


@pytest.fixture
def resume_submission_create_dto():
    return ResumeSubmissionCreateDto(
        recruiting_id=1, question_id=1, answer="test answer"
    )


@pytest.fixture
def resume_submission_update_dto():
    return ResumeSubmissionCreateDto(
        recruiting_id=1, question_id=1, answer="updated answer"
    )
