from datetime import datetime
from typing import List

import pytest
from sqlalchemy.orm import Session

from wacruit.src.apps.timeline.models import Timeline
from wacruit.src.apps.timeline.models import TimelineCategory
from wacruit.src.apps.timeline.models import TimelineGroupType
from wacruit.src.apps.timeline.repositories import TimelineRepository
from wacruit.src.apps.timeline.schemas import TimelineCategoryCreateUpdateRequest
from wacruit.src.apps.timeline.schemas import TimelineCreateRequest
from wacruit.src.apps.timeline.schemas import TimelineUpdateRequest
from wacruit.src.apps.timeline.services import TimelineService
from wacruit.src.apps.user.models import User
from wacruit.src.database.connection import Transaction


@pytest.fixture
def timeline_repository(db_session: Session):
    return TimelineRepository(session=db_session, transaction=Transaction(db_session))


@pytest.fixture
def timeline_service(timeline_repository: TimelineRepository) -> TimelineService:
    return TimelineService(timeline_repository=timeline_repository)


@pytest.fixture
def timeline_category1(db_session: Session) -> TimelineCategory:
    timeline_category = TimelineCategory(title="친목")
    db_session.add(timeline_category)
    db_session.commit()
    return timeline_category


@pytest.fixture
def timeline_category2(db_session: Session) -> TimelineCategory:
    timeline_category = TimelineCategory(title="세미나")
    db_session.add(timeline_category)
    db_session.commit()
    return timeline_category


@pytest.fixture
def created_category_list(db_session: Session) -> List[TimelineCategory]:
    category_list = []
    for i in range(0, 5):
        timeline_category = TimelineCategory(title=f"카테고리 {i}")
        db_session.add(timeline_category)
        category_list.append(timeline_category)
    db_session.commit()
    return category_list


@pytest.fixture
def created_timeline(
    db_session: Session, timeline_category1: TimelineCategory
) -> Timeline:
    timeline = Timeline(
        title="Created Timeline",
        group=TimelineGroupType.ROOKIE,
        category_id=timeline_category1.id,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 5),
    )
    db_session.add(timeline)
    db_session.commit()
    return timeline


@pytest.fixture
def created_timeline_list(
    db_session: Session, timeline_category1: TimelineCategory
) -> List[Timeline]:
    timeline_list = []

    for i in range(0, 5):
        timeline = Timeline(
            title=f"Created Timeline {i}",
            group=TimelineGroupType.ROOKIE,
            category_id=timeline_category1.id,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 5),
        )
        db_session.add(timeline)
        timeline_list.append(timeline)
    db_session.commit()
    return timeline_list


@pytest.fixture
def timeline_create_dto(timeline_category1: TimelineCategory) -> TimelineCreateRequest:
    return TimelineCreateRequest(
        title="New Timeline",
        group=TimelineGroupType.ROOKIE,
        category_id=timeline_category1.id,
        start_date=datetime(2025, 1, 1),
        end_date=datetime(2025, 1, 5),
    )


@pytest.fixture
def timeline_update_dto(timeline_category2: TimelineCategory) -> TimelineUpdateRequest:
    return TimelineUpdateRequest(
        title="Updated Timeline",
        group=TimelineGroupType.PROGRAMMER,
        category_id=timeline_category2.id,
        start_date=datetime(2025, 3, 1),
        end_date=datetime(2025, 3, 5),
    )


@pytest.fixture
def category_create_dto() -> TimelineCategoryCreateUpdateRequest:
    return TimelineCategoryCreateUpdateRequest(title="친목")


@pytest.fixture
def category_update_dto() -> TimelineCategoryCreateUpdateRequest:
    return TimelineCategoryCreateUpdateRequest(title="세미나")
