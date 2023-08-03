from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.announcement.repositories import AnnouncementRepository
from wacruit.src.apps.announcement.schemas import AnnouncementCreateDto
from wacruit.src.apps.announcement.services import AnnouncementService
from wacruit.src.apps.announcement.views import v1_router
from wacruit.src.apps.user.models import User
from wacruit.src.apps.user.repositories import UserRepository
from wacruit.src.database.connection import Transaction


@pytest.fixture
def user(db_session: Session) -> User:
    user = User(
        sso_id="abcdef123",
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="example@email.com",
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = User(
        sso_id="abcdef123",
        first_name="Test",
        last_name="User",
        phone_number="010-0000-0000",
        email="example@email.com",
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


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
