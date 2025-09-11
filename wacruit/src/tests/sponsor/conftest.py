import datetime
from typing import List

from pydantic import EmailStr
import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.sponsor.models import Sponsor
from wacruit.src.apps.sponsor.repositories import SponsorRepository
from wacruit.src.apps.sponsor.schemas import SponsorCreateRequest
from wacruit.src.apps.sponsor.schemas import SponsorUpdateRequest
from wacruit.src.apps.sponsor.services import SponsorService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def sponsor_repository(db_session: Session) -> SponsorRepository:
    return SponsorRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def sponsor_service(sponsor_repository: SponsorRepository) -> SponsorService:
    return SponsorService(sponsor_repository=sponsor_repository)


@pytest.fixture
def created_sponsor(db_session: Session) -> Sponsor:
    sponsor = Sponsor(
        name="김와플",
        amount=50000,
        email="waffle@snu.ac.kr",
        phone_number="010-1234-5678",
        sponsored_date=datetime.date(2025, 1, 1),
    )
    db_session.add(sponsor)
    db_session.commit()
    return sponsor


@pytest.fixture
def created_sponsor_list(db_session: Session) -> List[Sponsor]:
    sponsors = [
        Sponsor(
            name="김와플",
            amount=50000,
            email="waffle1@snu.ac.kr",
            phone_number="010-1111-1111",
            sponsored_date=datetime.date(2025, 1, 1),
        ),
        Sponsor(
            name="이와플",
            amount=200000,
            email="waffle2@snu.ac.kr",
            phone_number="010-2222-2222",
            sponsored_date=datetime.date(2025, 1, 1),
        ),
        Sponsor(
            name="최와플",
            amount=300000,
            email="waffle3@snu.ac.kr",
            phone_number="010-3333-3333",
            sponsored_date=datetime.date(2025, 1, 1),
        ),
    ]

    db_session.add_all(sponsors)
    db_session.commit()

    return sponsors


@pytest.fixture
def sponsor_create_dto():
    return SponsorCreateRequest(
        name="김와플",
        amount=100000,
        sponsored_date=datetime.date(2025, 1, 1),
        email=EmailStr("waffle@snu.ac.kr"),
        phone_number="010-1234-5678",
    )


@pytest.fixture
def sponsor_update_dto():
    return SponsorUpdateRequest(
        amount=1000000,
        email=EmailStr("waffle3@snu.ac.kr"),
        phone_number="010-2222-3333",
    )
