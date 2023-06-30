import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.announcement.repositories import AnnouncementRepository
from wacruit.src.apps.announcement.schemas import AnnouncementCreateDto
from wacruit.src.apps.announcement.services import AnnouncementService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def announcement_repository(db_session: Session):
    return AnnouncementRepository(
        session=db_session, transaction=Transaction(db_session)
    )


@pytest.fixture
def announcement_service(announcement_repository: AnnouncementRepository):
    return AnnouncementService(announcement_repository=announcement_repository)


@pytest.fixture
def announcement_create_dto():
    return AnnouncementCreateDto(
        title="Test Announcement", content="This is a test announcement."
    )


@pytest.fixture
def announcement_update_dto():
    return AnnouncementCreateDto(
        title="Updated Announcement", content="This is an updated test announcement."
    )
