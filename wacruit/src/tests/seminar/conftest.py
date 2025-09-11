from typing import List

import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.seminar.models import Seminar
from wacruit.src.apps.seminar.models import SeminarType
from wacruit.src.apps.seminar.repositories import SeminarRepository
from wacruit.src.apps.seminar.schemas import CreateSeminarRequest
from wacruit.src.apps.seminar.schemas import UpdateSeminarRequest
from wacruit.src.apps.seminar.services import SeminarService
from wacruit.src.database.connection import Transaction


@pytest.fixture
def created_active_seminar(db_session: Session) -> Seminar:
    seminar = Seminar(
        seminar_type=SeminarType("FASTAPI"),
        curriculum_info="FastAPI curriculum",
        prerequisite_info="Python",
        is_active=True,
    )
    db_session.add(seminar)
    db_session.commit()

    return seminar


@pytest.fixture
def created_not_active_seminar(db_session: Session) -> Seminar:
    seminar = Seminar(
        seminar_type=SeminarType("SPRING"),
        curriculum_info="Spring curriculum",
        prerequisite_info="Kotlin",
        is_active=False,
    )
    db_session.add(seminar)
    db_session.commit()

    return seminar


@pytest.fixture
def created_seminars(db_session: Session) -> List[Seminar]:
    seminar_list = []
    for i in range(5):
        seminar = Seminar(
            seminar_type=SeminarType("FASTAPI"),
            curriculum_info=f"curriculum {i}",
            prerequisite_info=f"{i}",
            is_active=True,
        )
        db_session.add(seminar)
        seminar_list.append(seminar)
    db_session.commit()

    return seminar_list


@pytest.fixture
def create_seminar_dto() -> CreateSeminarRequest:
    return CreateSeminarRequest(
        seminar_type=SeminarType("FASTAPI"),
        curriculum_info="New curriculum",
        prerequisite_info="Python",
        is_active=True,
    )


@pytest.fixture
def update_seminar_dto() -> UpdateSeminarRequest:
    return UpdateSeminarRequest(
        seminar_type=SeminarType("SPRING"),
        curriculum_info="Updated curriculum",
        prerequisite_info="Kotlin",
        is_active=False,
    )


@pytest.fixture
def seminar_service(seminar_repository: SeminarRepository) -> SeminarService:
    return SeminarService(seminar_repository=seminar_repository)


@pytest.fixture
def seminar_repository(db_session: Session) -> SeminarRepository:
    return SeminarRepository(session=db_session, transaction=Transaction(db_session))
